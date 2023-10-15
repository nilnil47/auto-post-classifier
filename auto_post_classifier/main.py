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
):
    openai.api_key = openai_api_key

    if api:
        from api import app
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    else:
        for ext in [".csv", ".txt"]:
            path_to_clear = output_dir / f"{output_base_filename}{ext}"
            logger.info(f"Checking if {path_to_clear} exists")
            if os.path.exists(path_to_clear) and not output_overwrite:
                logger.warning("Output paths exist but overwrite flag is false")
                raise typer.Exit(code=1)
            if os.path.exists(path_to_clear) and output_overwrite:
                logger.info(f"Removing the path {path_to_clear}")
                os.remove(path_to_clear)

        df = utils.load_csv(data_path)

        if shuffle:
            df = df.sample(frac=1)
        if post_num != -1:
            df = df.head(post_num)
        df["text"] = df["text"].fillna("")

        lst = []
        for i, text in enumerate(df["text"].head(post_num)):
            if text != "":
                logger.info(
                    f"------------------- {i} / {post_num} -------------------------"
                )
                logger.info(f"going the parse the following text:\n {text}")

                task = TaskBase(post=text)
                task.build_prompt()

                for j in range(iter_num + 1):
                    completion = utils.get_completion(task.prompt)

                    try:
                        response = json.loads(completion)
                    except JSONDecodeError:
                        logger.error("bad JSON format: %s", completion)
                        continue

                    if utils.check_JSON_format(response):
                        response["text"] = text
                        response["score"] = utils.generate_score(response)

                        with open(
                            output_dir / f"{output_base_filename}.txt",
                            "a",
                            encoding="utf-8",
                        ) as out_file:
                            out_file.write(f"{json.dumps(response, ensure_ascii=False)}\n")
                        lst.append(response)
                        break

        res = pd.DataFrame(lst)
        res.to_csv(output_dir / f"{output_base_filename}.csv")


if __name__ == "__main__":
    typer.run(main)
