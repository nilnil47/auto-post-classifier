import json
from json import JSONDecodeError

from fastapi import FastAPI
from loguru import logger
from pathlib import Path

import asyncio
import dotenv
import sys
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import auto_post_classifier.api as api

config = dotenv.dotenv_values()
api_manager = api.ApiManager(config)

logger.add(sys.stderr, format="{time} {level} {name}:{line} {message}")

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
     return api_manager


