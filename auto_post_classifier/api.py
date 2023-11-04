import json 

from pydantic import BaseModel
from models import TaskBase


import utils
import auto_post_classifier.gpt_handler as gpt_handler

import asyncio

from loguru import logger

class Post(BaseModel):
    text: str
    content_url: str

class JsonPosts(BaseModel):
    posts: dict[str, Post]

# class LLmManager:
#      def __init__(self) -> None:
#           self
#      def choose_llm(post: Post):
#           return gpt_handler.GptHandler(
#                text=post.text,
#                model="gpt-3.5-turbo-16k"
#           )


class PreRequestValidator:
     def __init__(self) -> None:
          pass

     def validate_length(self, post: Post):
          return len(post.text ) > 10

     def validate(self, post: Post):
          return True
     
class PostRequestValidator:
     def __init__(self) -> None:
          pass

     def validate_length(self, post: Post):
          return len(post.text ) > 10

     def validate():
          return 

class ApiManager:
     def __init__(self, config) -> None:
          self.__dict__.update(config)
          self.pre_request_validator = PreRequestValidator()
          self.post_request_validator = PostRequestValidator()
          self.gpt_handler = gpt_handler.GptHandler(
               responses_path="responses.txt",
               api_key=config['OPENAI_API_KEY']
          )
     
     def __str__(self) -> str:
          return json.dumps(self.__dict__, indent=2)
     
     async def process_posts(self, json_posts: dict[str, Post]):
          for uuid, post in json_posts.items():
               try:
                    if self.pre_request_validator.validate(post):
                         self.gpt_handler.add_request(uuid, post.text, gpt_handler.GPT_MODEL.GPT_3_5_16k)
                    await self.gpt_handler.send_requests()

               except Exception as e:
                    logger.error(f"Error while processing post {uuid}: {e}")