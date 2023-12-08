import os

import dotenv
from fastapi import FastAPI
from loguru import logger

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
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc",
)


@app.post("/rank")
async def process_posts(json_posts: dict[str, api.Post]):
    return await api_manager.process_posts(json_posts)


@app.get("/config")
def get_configuration():
    return api_manager.get_config()


# FIXME: does not really update the api_manager
@app.post("/config")
def update_config(edited_config: dict):
    config.update(edited_config)
    global api_manager
    api_manager = api.ApiManager(config)
