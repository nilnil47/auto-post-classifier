import os
import logging
from dataclasses import dataclass

import typer
# from rich import print
from rich.console import Console
from typing_extensions import Annotated
import pandas as pd

import utils
from models import TaskBase
import json

# todo: change the Path object
console = Console()

CSV_FILE = "AntiIsraeli.csv"
NUMBER_OF_POSTS = 100
    

def main():
    logging.basicConfig(level=logging.INFO)
    utils.set_openai_api_key()
    df = utils.load_csv(CSV_FILE)
    
    lst = []
    for i, text in enumerate(df["text"].head(NUMBER_OF_POSTS)):


        logging.info(f"------------------- {i} / {NUMBER_OF_POSTS} -------------------------")
        logging.info(f"going the parse the following text:\n {text}")

        task = TaskBase(post=text)
        task.build_prompt()

        console.print("About to send the following prompt🚀", style="#5f5fff")
        print(task.prompt)
        console.print("End of prompt", style="#5f5fff")

        response = json.loads(utils.get_completion(task.prompt))
        response["text"] = text

        lst.append(response)

    res = pd.DataFrame(lst)
    res.to_csv("result.csv")

if __name__ == "__main__":
    main()