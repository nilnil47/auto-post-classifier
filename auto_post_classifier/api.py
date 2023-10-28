import json
from json import JSONDecodeError

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel
from pathlib import Path
import auto_post_classifier.utils as utils
from auto_post_classifier.models import TaskBase

import asyncio
import typer


import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse



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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/rank")
def process_post(json_posts: dict[str, Post]):
    try:
        res_df = asyncio.run(
                utils.multiple_posts_loop_asunc(       
                    AutoPostCalassifierApi.openai_api_key,
                    json_posts,
                    AutoPostCalassifierApi.iter_num,
                    AutoPostCalassifierApi.base_path))
    except Exception as e:
        raise




