import json
from json import JSONDecodeError

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

import auto_post_classifier.utils as utils
from auto_post_classifier.models import TaskBase


class Post(BaseModel):
    text: str
    content_url: str

class JsonPosts(BaseModel):
    posts: dict[str, Post]

class AutoPostCalassifierApi(FastAPI):
    pass 

app = FastAPI()

@app.post("/rank")
def process_post(json_posts: JsonPosts):
    res_df = asyncio.run(
            multiple_posts_loop_asunc(       
                openai_api_key,
                post_num,
                response_out_paths,
                text_enum,
            )
        )
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


