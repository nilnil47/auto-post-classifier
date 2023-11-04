import json 

from pydantic import BaseModel
from models import TaskBase


import utils
import auto_post_classifier.gpt_handler as gpt_handler

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

     def validate():
          return 
     
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
     
     def __str__(self) -> str:
          return json.dumps(self.__dict__, indent=2)
     
     def process_posts(self, json_posts: dict[str, Post]):
          res_list = []
          uuids = []
          post_num = len(json_posts)

          user_prompts = []
            # todo we might want this as a List
          for uuid, post in json_posts.items():
               try:
                    if self.pre_request_validator.validate(post):
                         llm = 
                         prompt = gpt_handler.GptHandler(text=post.text, model="gpt-3.5-turbo-16k")
                         task = TaskBase(post=post.text)
                         task.build_prompt()
                         user_prompts.append((task.user_prompt, post.text))
                         uuids.append(uuid)
                         sys_prompt = task.sys_prompt
                         utils.create_gpt_request(
                              uuids, user_prompts, sys_prompt, openai_api_key, output_path=responses_path
    )
               except Exception as e:
                    logger.error(f"Error while processing post {uuid}: {e}")