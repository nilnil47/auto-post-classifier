import json
import jsonschema
import jinja2
from auto_post_classifier.api_request_parallel_processor import process_api_requests
from loguru import logger
from pathlib import Path

import auto_post_classifier.consts as consts

class GPT_MODEL:
    GPT_3_5_16k = "gpt-3.5-turbo-16k"
    GPT_4 = ""

class ResponseValidator:

    def __init__(self) -> None:
        self.validators = [
            self.validate_json,
            self.validate_explenation
        ]
        

    def validate_json(self, response_dict: dict):
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
        for dimension in consts.WEIGHTS:
            if response_dict[f"{dimension}_exp"] == f"-1, 0, or 1 ranking for {dimension}":
                logger.warning("validation error")
                return False
        return True        

    def validate(self, response: str)  -> (bool, str, dict) :
        try:
            response_dict = json.loads(response)
            for validator in self.validators:
                if not validator(response_dict):
                    return (False, validator.__name__, response_dict)

                return (True, "", response_dict)
            
        except Exception as e:
            logger.exception("validation exception:", e)
class GptHandler:

    def build_prompt(self, text):
        user_prompt = self.user_prompt_template.render(text=text)
        sys_prompt = self.system_prompt_template.render()
        return (user_prompt, sys_prompt)
    
    def choose_prompt_template(self, user_template_path: str, system_template_path: str):
        self.user_prompt_template = self.jinja_environment.get_template(user_template_path)
        self.system_prompt_template = self.jinja_environment.get_template(system_template_path)

        
    def __init__(self, responses_path: Path, api_key: str, mock_file: str = None) -> None:
        self.requests = []
        self.responses_path : Path = responses_path
        self.api_key : str = api_key
        self.response_validator : ResponseValidator = ResponseValidator()
        self.mock_file : str = mock_file
        self.jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader("prompts"),
            autoescape=jinja2.select_autoescape()
        )
        self.choose_prompt_template(
            "gpt3_5_user.prompt",
            "gpt3_5_system.prompt"
        )

        self._handle_mock()
    
    def _handle_mock(self):
        if self.mock_file is not None:
            logger.warning(f"using mock response file: {self.mock_file}")
            self.responses_path = Path(self.mock_file)

    def add_request(self, uuid: str, text: str, model: GPT_MODEL) -> None:
        
        user_prompt, sys_prompt = self.build_prompt(text)
        self.requests.append(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "metadata": {"text": text, "uuid": uuid}
        })
    
    async def send_requests(self):
        logger.info(f"process {len(self.requests)} requests")
        if self.mock_file is None:
            await process_api_requests(self.requests, self.responses_path, self.api_key)
    
    def read_responses(self):
        """returns the responses generated by the async completion. returns the data
        in a sorted manner according to the metadata."""

        responses_dict = {}
        with open(self.responses_path, "r") as file:
            for line in file:
                full_response : dict = json.loads(line)
                completion_response : str = full_response[1]["choices"][0]["message"]["content"]
                metadata = full_response[2]
                
                validation, reasone, completion_response_dict = self.response_validator.validate(completion_response)
                if validation:
                    uuid, response = self.handle_validate_response(
                        metadata,
                        completion_response_dict
                    )
                else:
                    uuid, response = self.handle_bad_validation(reasone, metadata, completion_response_dict)

                responses_dict[uuid] = response
    
        return responses_dict
    
    def handle_bad_validation(self, reason: str, metadata: dict, completion_response_dict: dict):
        completion_response_dict["text"] = metadata["text"]
        completion_response_dict["error"] = reason
        uuid = metadata["uuid"]
        self._dump_invalid_json(uuid, completion_response_dict)
        return uuid, completion_response_dict

    def handle_validate_response(self, metadata: dict, completion_response_dict: dict):
        completion_response_dict["text"] = metadata["text"]
        completion_response_dict["error"] = ""
        completion_response_dict["score"] = self.calculate_score(completion_response_dict)
        return metadata["uuid"], completion_response_dict
    
    def calculate_score(self, completion_response_dict: dict):
        
        rnk_mtpl_map = {-1: -0.2, 0: 0.2, 1: 1}
        score = 0

        for dimension in consts.WEIGHTS:
            score += rnk_mtpl_map[int(completion_response_dict[dimension + "_rnk"])] * consts.WEIGHTS[dimension]
        
        score = round(score, 3)

        return score
    
    def _dump_invalid_json(self, uuid: str, completion_response_dict: dict):
        if not consts.INVALID_JSON_RESPONSES_DIR.exists():
            consts.INVALID_JSON_RESPONSES_DIR.mkdir()
        with open(consts.INVALID_JSON_RESPONSES_DIR / uuid, "w") as f:
            json.dump(completion_response_dict, f)
