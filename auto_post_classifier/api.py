import json
from json import JSONDecodeError

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel
from pathlib import Path
import auto_post_classifier.utils as utils
from auto_post_classifier.models import TaskBase

import asyncio


class Post(BaseModel):
    text: str
    content_url: str

class JsonPosts(BaseModel):
    posts: dict[str, Post]

class AutoPostCalassifierApi(FastAPI):
    @staticmethod
    def set_params(openai_api_key: str, base_path: Path, iter_num: int):
        AutoPostCalassifierApi.openai_api_key = openai_api_key
        AutoPostCalassifierApi.base_path = base_path,
        AutoPostCalassifierApi.iter_num = iter_num,

app = AutoPostCalassifierApi()

@app.post("/rank")
def process_post(json_posts: JsonPosts):
    res_df = asyncio.run(
            utils.multiple_posts_loop_asunc(       
                AutoPostCalassifierApi.openai_api_key,
                json_posts,
                AutoPostCalassifierApi.iter_num,
                AutoPostCalassifierApi.base_path))
    
    
    for post in json_posts:
        task = TaskBase(post=post.text)
        task.build_prompt()

        # fixme: replace to iternum
        for j in range(iter_num + 1):
            completion = utils.get_completion(
                user_prompt=task.user_prompt, sys_prompt=task.sys_prompt
            )

            try:
                response = json.loads(completion)
            except JSONDecodeError:
                logger.error("bad JSON format: %s", completion)
                continue

            if utils.JSON_rank_to_number(response) and utils.check_JSON_format(response):
                response["text"] = post.text
                response["score"] = utils.generate_score(response)
                return response

        logger.error("fail to process responses after all attempts")


