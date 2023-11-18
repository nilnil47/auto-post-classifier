import json
import os
from json import JSONDecodeError

from fastapi import FastAPI
from loguru import logger

import dotenv
import sys
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import auto_post_classifier.api as api
import auto_post_classifier.consts as consts

def load_config():
    config = consts.DEFULAT_ENV
    config.update(dotenv.dotenv_values())
    print(config)
    return config

config = load_config()
api_manager = api.ApiManager(config)

if not os.path.exists("logs"):
     os.mkdir("logs")
     
logger.add(os.path.join("logs", "file_{time}.log"))

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

@app.get('/config')
def get_configuration():
     return api_manager.get_config()

# FIXME: does not really update the api_manager
@app.get('/reconfig')
def reconfig():
      config = load_config()
      global api_manager
      api_manager = api.ApiManager(config)
      return config


