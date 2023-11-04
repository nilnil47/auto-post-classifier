import json
from json import JSONDecodeError

from fastapi import FastAPI
from loguru import logger
from pathlib import Path
import auto_post_classifier.utils as utils
from auto_post_classifier.models import TaskBase

import asyncio
import dotenv

import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import auto_post_classifier.api as api

config = dotenv.dotenv_values()
api_manager = api.ApiManager(config)



app = FastAPI(
    title="auto post classifier",
    description="Description of my app.",
    version="1.0",
    docs_url='/docs',
    openapi_url='/openapi.json',
    redoc_url="/redoc"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/rank")
async def process_posts(json_posts: dict[str, api.Post]):
    return await api_manager.process_posts(json_posts)
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
     return api_manager


