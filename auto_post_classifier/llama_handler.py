import json
import os
from pathlib import Path
from typing import Optional

import jinja2
import jsonschema
from loguru import logger
import ollama

from .consts import DEFAULT_INVALID_JSON_RESPONSES, DEFAULT_PROMPTS_PATH, WEIGHTS
from .utils import generate_uuid


class LLAMA_MODEL:
    LLAMA_3_2 = "llama3.2"


class LLAMA_ERROR_REASONS:
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


class LlamaHandler:
    MODEL = LLAMA_MODEL.LLAMA_3_2
    def __str__(self) -> str:
        return json.dumps(
            {
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
        mock_file: Optional[str] = None,
        invalid_json_responses_dir=None,
        user_template: str = "llama_user.prompt",
        system_template: str = "llama_system.prompt",
        prompts_dir_path: str = None,  # type: ignore
    ) -> None:
        self.requests: list[dict] = []
        self.responses_path: Path = responses_path
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

        logger.warning(f"mock file: {self.mock_file}")

        self._clean_response_path()
        self._handle_mock()

    def _clean_response_path(self):
        return
        if self.responses_path.exists():
            self.responses_path.unlink()

    def _handle_mock(self):
        if self.mock_file is not None:
            logger.warning(f"using mock response file: {self.mock_file}")
            self.responses_path = Path(self.mock_file)

    def add_request(self, uuid: str, text: str) -> None:
        user_prompt, sys_prompt = self.build_prompt(text)
        print("--------------------------------")
        print(self.MODEL)
        self.requests.append(
            {
                "model": self.MODEL,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "metadata": {"text": text, "uuid": uuid},
            }
        )

    async def send_requests(self):
        logger.info(f"process {len(self.requests)} requests")
        if self.mock_file is None:
            responses = []
            for request in self.requests:
                response = ollama.chat(
                    model=request["model"],
                    messages=[
                        {"role": "system", "content": request["messages"][0]["content"]},
                        {"role": "user", "content": request["messages"][1]["content"]},
                    ],
                )
                responses.append([request["metadata"], response["message"]["content"]])
            
            with open(self.responses_path, "w") as f:
                print("--------------------------------")
                print(self.responses_path)
                for response in responses:
                    json.dump(response, f)
                    f.write("\n")

    # The rest of the methods (read_responses, _handle_parsing_error, handle_bad_validation, 
    # handle_validate_response, calculate_score, _dump_invalid_json) remain the same as in GptHandler

    # ... (include the rest of the methods here)

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

    def _read_single_response(self, line: str):
            full_response: list = json.loads(line)
            metadata = full_response[-1]
            uuid = metadata["uuid"]
            response = metadata["text"]
            self.responses_dict[uuid] = response
