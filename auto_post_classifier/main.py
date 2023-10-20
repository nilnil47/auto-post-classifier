import datetime
import json
import os
from json import JSONDecodeError

import pandas as pd
import typer
from typing_extensions import Annotated
from loguru import logger
from rich.console import Console
from pathlib import Path
from auto_post_classifier import utils
from auto_post_classifier.models import TaskBase

import openai
import uvicorn


# todo: change the Path object
console = Console()
logger.add("file_{time}.log")


def main(
    data_path: Annotated[
        Path,
        typer.Option(
            "--data-path",
            "-d",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            # To force overwite
            exists=False,
            file_okay=False,
            dir_okay=True,
            writable=True,
            resolve_path=True,
            help="Path (dir) where results should be persisted",
        ),
    ] = "./output",
    output_base_filename: Annotated[
        str,
        typer.Option(
            help=(
                "Base filename for the outputs. Two files will be created, .txt for the"
                " persistance of results during the run and .csv for the final result"
                " (upon successful completion)"
            )
        ),
    ] = "result",
    post_num: Annotated[
        int,
        typer.Option(
            "--post-num",
            "-n",
            help=(
                "Set the number of posts to be processed from the list. Use -1 if you"
                " want to process all posts in the data"
            ),
        ),
    ] = 100,
    iter_num: Annotated[
        int, typer.Option("--iter-num", "-i", help="Number of attempts upon failure")
    ] = 2,
    shuffle: Annotated[
        bool, typer.Option(help="Turn shuffling of data on or off")
    ] = True,
    output_overwrite: Annotated[
        bool, typer.Option(help="Whether to overwrite results or not")
    ] = False,
    api: Annotated[
        bool, typer.Option(help="Wheter to use api mode")
    ] = False,
    openai_api_key: Annotated[
        str, typer.Option(help="API key for OpenAI", envvar="OPENAI_API_KEY")
    ] = ...,
    min_post_length: int = typer.Option(
        0,  # Default min_length value
        help="Minimum length for filtering posts",
    ),
):
    openai.api_key = openai_api_key
    base_path =Path("")


    if api:
        from api import app
        uvicorn.run(app, host="0.0.0.0", port=8000)

    else:
        for ext in [".csv", ".txt"]:
            path_to_clear = Path(base_path) / output_dir / f"{output_base_filename}{ext}"
            logger.info(f"Checking if {path_to_clear} exists")
            if os.path.exists(path_to_clear) and not output_overwrite:
                logger.warning("Output paths exist but overwrite flag is false")
                raise typer.Exit(code=1)
            if os.path.exists(path_to_clear) and output_overwrite:
                logger.info(f"Removing the path {path_to_clear}")
                os.remove(path_to_clear)

        df = utils.load_csv(data_path)
        df = df[df['text'].str.len() >= min_post_length]

        if shuffle:
            df = df.sample(frac=1)
        if post_num != -1:
            df = df.head(post_num)
        df["text"] = df["text"].fillna("")

        response_out_paths =[]

        text_enum = df["text"]
        res_df = pd.DataFrame()

        for i in range(iter_num):
            user_prompts=[]
            sys_prompt = ""  # todo we might want this as a List
            for i, text in enumerate(text_enum):
                if text != "":
                    logger.info(
                        f"------------------- {i} / {post_num} -------------------------"
                    )
                    logger.info(f"going the parse the following text:\n {text}")

                    task = TaskBase(post=text)
                    task.build_prompt()
                    user_prompts.append((task.user_prompt, text))
                    sys_prompt = task.sys_prompt
            if len(text_enum):
                current_datetime = datetime.datetime.now()
                formatted_datetime = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')
                responses_path = base_path / f"responses_{formatted_datetime}.txt"
                response_out_paths.append(responses_path)
                utils.create_completion_async(user_prompts, sys_prompt, openai_api_key, output_path=responses_path)
                res_list, text_enum = utils.parse_parallel_responses(utils.read_parallel_response(responses_path))
                res_df = pd.concat([res_df, pd.DataFrame(res_list)], ignore_index=True)

        for path in response_out_paths:
            if os.path.exists(path):
                logger.debug(f"Removing the path {path}")
                os.remove(path)

        res_df.to_csv(base_path / output_dir / f"{output_base_filename}.csv")


if __name__ == "__main__":
    typer.run(main)
