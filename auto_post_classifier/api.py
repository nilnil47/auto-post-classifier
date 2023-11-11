import json 

from pydantic import BaseModel

import pathlib
import auto_post_classifier.gpt_handler as gpt_handler

import asyncio

from loguru import logger
import auto_post_classifier.response_logger as response_logger
import consts

class Post(BaseModel):
    text: str
    content_url: str

class JsonPosts(BaseModel):
    posts: dict[str, Post]

# this calls is not really used right now
# but it is here for show to consept of
# the prerequest validator
# now the validation is allways true
class PreRequestValidator:
     def __init__(self) -> None:
          pass

     def validate_length(self, post: Post):
          return len(post.text ) > 10

     def validate(self, post: Post):
          return True
     

class ApiManager:
     def __init__(self, config) -> None:
          self.__dict__.update(config)
          self.pre_request_validator = PreRequestValidator()
          self.gpt_handler = gpt_handler.GptHandler(
               responses_path="responses.txt",
               api_key=config["OPENAI_API_KEY"],
               mock_file=config["MOCK_FILE"]
          )
          self.response_logger = response_logger.ResponseLogger(
               pathlib.Path(config["RESPONSES_DIR"]),
               consts.RESPONSE_LOGGER_KEYS
          )
     
     def __str__(self) -> str:
          return json.dumps(self.__dict__, indent=2)
     
     @logger.catch
     async def process_posts(self, json_posts: dict[str, Post]):
          for uuid, post in json_posts.items():
               if self.pre_request_validator.validate(post):
                    self.gpt_handler.add_request(uuid, post.text, gpt_handler.GPT_MODEL.GPT_3_5_16k)

          await self.gpt_handler.send_requests()
          response = self.gpt_handler.read_responses()
          self.response_logger.log_response(response)
          return response
     
          