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
               api_key=config['OPENAI_API_KEY']
          )
     
     def __str__(self) -> str:
          return json.dumps(self.__dict__, indent=2)
     
     @logger.catch
     async def process_posts(self, json_posts: dict[str, Post]):
          for uuid, post in json_posts.items():
               if self.pre_request_validator.validate(post):
                    self.gpt_handler.add_request(uuid, post.text, gpt_handler.GPT_MODEL.GPT_3_5_16k)

          await self.gpt_handler.send_requests()
          return self.gpt_handler.read_responses()