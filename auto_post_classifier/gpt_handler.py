import json
import jsonschema
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
        user_prompt = f"""Here is some context:
@@In recent news, a bold and unprecedented attack was carried out by the Palestinian militant group Hamas against Israel.
This egregious assault involved approximately 3,000 assailants infiltrating Israeli territory,
resulting in numerous casualties, including both soldiers and civilians. Dozens of hostages were also abducted.
The attack has been marked by extreme brutality, with disturbing reports of massacres, beheadings, sexual violence,
and the use of civilians as human shields. These actions have been widely condemned as war crimes and crimes against
humanity under international humanitarian law.@@

The result should be provided as a JSON with the following format:

{{
    "antisemitism_exp": "Explanation regarding the presence of antisemitic content",
    "antisemitism_rnk": "-1, 0, or 1 ranking for antisemitism",

    "antiIsrael_extremist_exp": "Explanation regarding the presence of anti-Israel extremist content",
    "antiIsrael_extremist_rnk": "-1, 0, or 1 ranking for anti-Israel extremism",

    "graphic_violence_exp": "Explanation regarding the presence of graphic violence content",
    "graphic_violence_rnk": "-1, 0, or 1 ranking for graphic violence",

    "weapons_exp": "Explanation regarding the presence of content related to weapons",
    "weapons_rnk": "-1, 0, or 1 ranking for weapons content",

    "calls_for_violence_exp": "Explanation regarding the presence of content related to a call for violence operation",
    "calls_for_violence_rnk": "-1, 0, or 1 ranking for a call for violence operation",

    "endorsement_of_terrorism_exp": "Explanation regarding the presence of content supporting terrorism",
    "endorsement_of_terrorism_rnk": "-1, 0, or 1 ranking for support of terrorism",

    "misinformation_exp": "Explanation regarding the presence of misinformation",
    "misinformation_rnk": "-1, 0, or 1 ranking for misinformation",

    "summary": "Summary of the post in a maximum of 3 lines"
}}

```
{text}
``` 
"""
        sys_prompt = """You are helping to keep the internet safe.
You're tasked with evaluating a post enclosed by three backticks to rank it in the following dimensions:
- antisemitism
- anti-Israel extremism
- graphic violence
- weapons
- calls for violence
- endorsement of terrorism
- misinformation

Use the ranking system:
-1: The dimension is not present in the post.
0: It's unclear if the dimension is in the post.
1: The dimension is highly likely to be in the post.

Provide an explanation for each ranking.
"""  # noqa: E501
        return (user_prompt, sys_prompt)
        
    def __init__(self, responses_path: Path, api_key: str, mock_file: str = None) -> None:
        self.requests = []
        self.responses_path : Path = responses_path
        self.api_key : str = api_key
        self.response_validator : ResponseValidator = ResponseValidator()
        self.mock_file : str = mock_file

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
