import json
import os
import pathlib

from loguru import logger

import auto_post_classifier.consts as consts
import auto_post_classifier.gpt_handler as gpt_handler
import auto_post_classifier.response_persister as response_persister

from .models import Post
from .utils import get_var_from_env


# this calls is not really used right now
# but it is here for show to consept of
# the prerequest validator
# now the validation is allways true
class PreRequestValidator:
    def __init__(self) -> None:
        pass

    def validate_length(self, post: Post):
        return len(post.text) > 10

    def validate(self, post: Post):
        return True


class ApiManager:
    def get_config(self):
        return {
            "gpt": str(self.gpt_handler),
            "response_persister": self.response_persister,
        }

    def __init__(self) -> None:
        self.pre_request_validator = PreRequestValidator()
        self.gpt_handler = gpt_handler.GptHandler(
            responses_path=pathlib.Path("responses.txt"),
            api_key=os.environ["OPENAI_API_KEY"],
            mock_file=get_var_from_env("MOCK_FILE"),
        )
        self.response_persister = response_persister.ResponsePersister(
             pathlib.Path(os.environ["RESPONSES_DIR"]), consts.RESPONSE_PERSISTER_KEYS
        )

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=2)

    @logger.catch
    async def process_posts(self, json_posts: dict[str, Post]):
        for uuid, post in json_posts.items():
            if self.pre_request_validator.validate(post):
                self.gpt_handler.add_request(
                    uuid, post.text, gpt_handler.GPT_MODEL.GPT_3_5_16k
                )

        await self.gpt_handler.send_requests()
        response = self.gpt_handler.read_responses()

        if (len(json_posts)) != len(response):
            logger.warning(
                f"the number of request and response posts are not equale "
                f"send {len(json_posts)} posts and got {len(response)} response"
            )

        # self.response_persister.persist_response(response)
        self.gpt_handler._clean_response_path()
        json_posts.clear()
        return response
