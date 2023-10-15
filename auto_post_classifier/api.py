from fastapi import FastAPI
from auto_post_classifier.models import TaskBase
import auto_post_classifier.utils
import json
from json import JSONDecodeError
from loguru import logger

from pydantic import BaseModel

class Post(BaseModel):
    text: str
    content_url: str


iter_num = 2 
app = FastAPI()

@app.post("/rank")
def read_root(post: Post):
    task = TaskBase(post=post.text)
    task.build_prompt()

    # fixme: replace to iternum 
    for j in range(iter_num + 1):
        completion = utils.get_completion(task.prompt)

        try:
            response = json.loads(completion)
        except JSONDecodeError:
            logger.error("bad JSON format: %s", completion)
            continue

        if utils.check_JSON_format(response):
            response["text"] = post.text
            response["score"] = utils.generate_score(response)
            return response

    

