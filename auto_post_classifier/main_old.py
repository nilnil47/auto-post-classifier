import asyncio
import datetime
import os
from pathlib import Path

import openai
import pandas as pd
import uvicorn
from dotenv import load_dotenv, dotenv_values
from loguru import logger
from rich.console import Console
from typing_extensions import Annotated

from auto_post_classifier import utils
from auto_post_classifier.models import TaskBase


# todo: change the Path object
config = dotenv_values()
console = Console()
logger.add(os.path.join("logs", "file_{time}.log"))




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
        bool, typer.Option(help="Whether to overwrite results or not", envvar="OUTPUT_OVERIDE")
    ] = False,
    api: Annotated[
        bool, typer.Option(help="Wheter to use api mode", envvar="API")
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
    base_path = Path("")

    if api:
        from auto_post_classifier.main import app, AutoPostCalassifierApi
        print('---------------- inter apiiiiiiii:', iter_num)
        # todo: understand why typer give these values as tuple
        # AutoPostCalassifierApi.set_params(openai_api_key, base_path, iter_num)
        AutoPostCalassifierApi.iter_num = 1
        AutoPostCalassifierApi.base_path = base_path
        AutoPostCalassifierApi.openai_api_key = openai_api_key

        uvicorn.run(app, host="0.0.0.0", port=80)
        typer.Exit(0)

    else:
        for ext in [".csv", ".txt"]:
            path_to_clear = (
                Path(base_path) / output_dir / f"{output_base_filename}{ext}"
            )
            logger.info(f"Checking if {path_to_clear} exists")
            if os.path.exists(path_to_clear) and not output_overwrite:
                logger.warning("Output paths exist but overwrite flag is false")
                raise typer.Exit(code=1)
            if os.path.exists(path_to_clear) and output_overwrite:
                logger.info(f"Removing the path {path_to_clear}")
                os.remove(path_to_clear)

        df = utils.load_csv(data_path)
        df = df[df["text"].str.len() >= min_post_length]

        if shuffle:
            df = df.sample(frac=1)
        if post_num != -1:
            df = df.head(post_num)
        df["text"] = df["text"].fillna("")

        response_out_paths = []
        text_enum = df["text"]

        res_df = asyncio.run(
            main_loop_async(
                base_path,
                iter_num,
                openai_api_key,
                post_num,
                response_out_paths,
                text_enum,
            )
        )

        # delete the response_{DT}.txt files that were created
        for path in response_out_paths:
            if os.path.exists(path):
                logger.debug(f"Removing the path {path}")
                os.remove(path)

        res_df.to_csv(base_path / output_dir / f"{output_base_filename}.csv")


async def main_loop_async(
    base_path, iter_num, openai_api_key, post_num, response_out_paths, posts_enum
):
    """asynchronous. Generates gpt responses for all posts in 'posts_enum'.
    returns the results as data frame."""

    res_df = pd.DataFrame()
    uuids = []

    print('---------------- inter:', iter_num)
    for j in range(iter_num):
        user_prompts = []
        sys_prompt = ""  # todo we might want this as a List
        for i, text in enumerate(posts_enum):
            if text != "":
                logger.info(
                    f"------------------- {i} / {post_num} -------------------------"
                )
                logger.info(f"going the parse the following text:\n {text}")

                task = TaskBase(post=text)
                task.build_prompt()
                user_prompts.append((task.user_prompt, text))
                uuids.append(i)
                sys_prompt = task.sys_prompt
        if len(posts_enum):
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            responses_path = base_path / f"responses_{formatted_datetime}.txt"
            response_out_paths.append(responses_path)
            await utils.create_completion_async(
                uuids, user_prompts, sys_prompt, openai_api_key, output_path=responses_path
            )
            res_list, posts_enum = utils.parse_parallel_responses(
                utils.read_parallel_response(responses_path), from_api=False
            )
            res_df = pd.concat([res_df, pd.DataFrame(res_list)], ignore_index=True)
    return res_df


if __name__ == "__main__":
    typer.run(main)
