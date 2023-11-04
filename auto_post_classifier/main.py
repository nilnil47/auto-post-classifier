import json
from json import JSONDecodeError

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel
from pathlib import Path
import auto_post_classifier.utils as utils
from auto_post_classifier.models import TaskBase

import asyncio
import dotenv

import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiManager:
     def __init__(self, config) -> None:
          self.__dict__.update(config)

     def test():
          return 5
     
     def __str__(self) -> str:
          return json.dumps(self.__dict__, indent=2)

config = dotenv.dotenv_values()
apiManager = ApiManager(config)
class Post(BaseModel):
    text: str
    content_url: str

class JsonPosts(BaseModel):
    posts: dict[str, Post]


app = FastAPI(
    title="auto post classifier",
    description="Description of my app.",
    version="1.0",
    docs_url='/docs',
    openapi_url='/openapi.json', # This line solved my issue, in my case it was a lambda function
    redoc_url="/redoc"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/rank")
async def process_posts(json_posts: dict[str, Post]):
    pass
    # try:
    #     res_list = await utils.multiple_posts_loop_asunc(       
    #                 AutoPostCalassifierApi.openai_api_key,
    #                 json_posts,
    #                 AutoPostCalassifierApi.iter_num,
    #                 AutoPostCalassifierApi.base_path)
    # except Exception as e:
    #     raise
    # return res_list

@app.get('/config')
def get_configuration():
     return apiManager


