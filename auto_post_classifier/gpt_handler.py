import json
import os
from pathlib import Path
from typing import Optional

import jinja2
import jsonschema
from loguru import logger

from .api_request_parallel_processor import process_api_requests
from .consts import DEFAULT_INVALID_JSON_RESPONSES, DEFAULT_PROMPTS_PATH, WEIGHTS
from .utils import generate_uuid


# todo: from python 3.11 its is possible to use string enums
class GPT_MODEL:
    GPT_3_5_16k = "gpt-3.5-turbo-16k"


class GPT_ERROR_REASONS:
    TO_MANY_REQUESTS = "many_requests"
    JSON_VALIDARTION = "validate_json"
    CANT_OPEN_RESPONSE_JSON = "cant_open_response_json"


class ResponseValidator:
    def __init__(self) -> None:
        self.validators = [self.validate_json_schema, self.validate_explenation]

    def validate_json_schema(self, response_dict: dict):
        # Define the JSON schema
        schema = {
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "patternProperties": {
                ".*_exp$": {"type": "string"},
                ".*_rnk$": {"enum": [0, 1, -1, "0", "1", "-1"]},
            },
            "additionalProperties": False,
            "required": ["summary"],
        }

        # Validate the JSON data against the schema
        try:
            jsonschema.validate(instance=response_dict, schema=schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.warning(f"JSON is not valid: {e.message}")
            return False

    def validate_explenation(self, response_dict: dict):
        for dimension in WEIGHTS:
            if (
                response_dict[f"{dimension}_exp"]
                == f"-1, 0, or 1 ranking for {dimension}"
            ):
                logger.warning("validation error")
                return False
        return True

    def validate(self, response: str) -> tuple[bool, str, dict]:
        response_dict = json.loads(response)
        for validator in self.validators:
            if not validator(response_dict):
                return (False, validator.__name__, response_dict)

        return (True, "", response_dict)


class GptHandler:
    def __str__(self) -> str:
        return json.dumps(
            {
                "api_key": self.api_key,
                "mock_file": self.mock_file,
            }
        )

    def build_prompt(self, text):
        user_prompt = self.user_prompt_template.render(text=text)
        sys_prompt = self.system_prompt_template.render()
        return (user_prompt, sys_prompt)

    def __init__(
        self,
        responses_path: Path,
        api_key: str,
        mock_file: Optional[str] = None,
        invalid_json_responses_dir=None,
        user_template: str = "gpt3_5_user.prompt",
        system_template: str = "gpt3_5_system.prompt",
        prompts_dir_path: str = None,  # type: ignore
    ) -> None:
        self.requests: list[dict] = []
        self.responses_path: Path = responses_path
        self.api_key: str = api_key
        self.response_validator: ResponseValidator = ResponseValidator()
        self.mock_file: Optional[str] = mock_file

        if prompts_dir_path is None:
            prompts_dir_path = os.environ.get("PROMPTS_PATH", DEFAULT_PROMPTS_PATH)

        self.jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(prompts_dir_path),
            autoescape=jinja2.select_autoescape(),
        )
        self.user_prompt_template = self.jinja_environment.get_template(user_template)
        self.system_prompt_template = self.jinja_environment.get_template(
            system_template
        )

        if invalid_json_responses_dir is None:
            invalid_json_responses_dir = os.environ.get(
                "INVALID_JSON_RESPONSES_DIR", DEFAULT_INVALID_JSON_RESPONSES
            )

        self.invalid_json_responses_dir: Path = Path(invalid_json_responses_dir)

        logger.warning(f"api key: {self.api_key}")
        logger.warning(f"mock file: {self.mock_file}")

        self._clean_response_path()
        self._handle_mock()

    def _clean_response_path(self):
        if self.responses_path.exists():
            self.responses_path.unlink()

    def _handle_mock(self):
        if self.mock_file is not None:
            logger.warning(f"using mock response file: {self.mock_file}")
            self.responses_path = Path(self.mock_file)

    def add_request(self, uuid: str, text: str, model: str) -> None:
        user_prompt, sys_prompt = self.build_prompt(text)
        self.requests.append(
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "metadata": {"text": text, "uuid": uuid},
            }
        )

    def reset_requests(self):
        self.requests = []

    async def send_requests(self):
        logger.info(f"process {len(self.requests)} requests")
        if self.mock_file is None:
            await process_api_requests(self.requests, self.responses_path, self.api_key)

    def _read_single_response(self, line: str):
        try:  # when getting wrong json from open ai, probably mocking problem
            full_response: list = json.loads(line)
        except json.decoder.JSONDecodeError:
            uuid = generate_uuid()
            response = self._handle_parsing_error(
                line, uuid, GPT_ERROR_REASONS.CANT_OPEN_RESPONSE_JSON
            )
            self.responses_dict[uuid] = response
            return

        # the metada is the last entry
        try:
            metadata = full_response[-1]
            uuid = metadata["uuid"]
        except TypeError:
            uuid = generate_uuid()

        try:
            completion_response: str = full_response[1]["choices"][0]["message"][
                "content"
            ]

        except TypeError:  # happens when getting to the tokens max capacity
            response = self.handle_bad_validation(
                GPT_ERROR_REASONS.TO_MANY_REQUESTS, metadata, {}
            )
            self.responses_dict[uuid] = response
            return

        try:
            (
                validation,
                reasone,
                completion_response_dict,
            ) = self.response_validator.validate(completion_response)

        except json.decoder.JSONDecodeError:
            metadata
            response = self.handle_bad_validation(
                GPT_ERROR_REASONS.JSON_VALIDARTION, metadata, {}
            )
            self.responses_dict[uuid] = response
            return

        if validation:
            response = self.handle_validate_response(metadata, completion_response_dict)
        else:
            response = self.handle_bad_validation(
                reasone, metadata, completion_response_dict
            )

        self.responses_dict[uuid] = response

    def read_responses(self):
        """returns the responses generated by the async completion. returns the data
        in a sorted manner according to the metadata."""

        self.responses_dict = {}
        with open(self.responses_path, "r") as file:
            for line in file:
                self._read_single_response(line)

        return self.responses_dict

    def _handle_parsing_error(
        self, response: dict | list | str, uuid=None, reason="unknow"
    ):
        if uuid is None:
            uuid = generate_uuid()

        logger.error(f"bad parsing for {uuid}: {reason}")
        inner_dir: Path = self.invalid_json_responses_dir / reason

        if not inner_dir.exists():
            inner_dir.mkdir(parents=True)

        file_name = f"{uuid}.json"

        with open(inner_dir / file_name, "w") as f:
            if isinstance(response, dict) or isinstance(response, list):
                json.dump(response, f)
            elif isinstance(response, str):
                f.write(response)
            else:
                logger.error(
                    f"unkwon response type for {uuid}. type is: {type(response)}"
                )

        return {"error": reason, "uuid": uuid}

    def handle_bad_validation(
        self, reason: str, metadata: dict, completion_response_dict: dict
    ):
        completion_response_dict["text"] = metadata["text"]
        completion_response_dict["error"] = reason
        uuid = metadata["uuid"]
        self._handle_parsing_error(completion_response_dict, uuid=uuid, reason=reason)
        return completion_response_dict

    def handle_validate_response(self, metadata: dict, completion_response_dict: dict):
        completion_response_dict["text"] = metadata["text"]
        completion_response_dict["error"] = ""
        completion_response_dict["score"] = self.calculate_score(
            completion_response_dict
        )
        return completion_response_dict

    def calculate_score(self, completion_response_dict: dict):
        rnk_mtpl_map = {-1: 0, 0: 0.5, 1: 1}
        score = 0

        for dimension in WEIGHTS:
            score += (
                rnk_mtpl_map[int(completion_response_dict[dimension + "_rnk"])]
                * WEIGHTS[dimension]
            )

        score = round(score, 3)

        return score

    def _dump_invalid_json(self, uuid: str, completion_response_dict: dict | str):
        if not self.invalid_json_responses_dir.exists():
            self.invalid_json_responses_dir.mkdir()

        with open(self.invalid_json_responses_dir / uuid, "w") as f:
            json.dump(completion_response_dict, f)
