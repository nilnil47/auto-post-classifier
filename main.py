import os

import dotenv
from fastapi import FastAPI
from loguru import logger

import auto_post_classifier.api as api

dotenv.load_dotenv()
api_manager = api.ApiManager()

if not os.path.exists("logs"):
    os.mkdir("logs")

logger.add(os.path.join("logs", "file_{time}.log"))
logger.info(api_manager.get_config())

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
