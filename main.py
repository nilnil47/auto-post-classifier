import os
import logging
from dataclasses import dataclass

import typer
# from rich import print
from rich.console import Console
from typing_extensions import Annotated

import utils
from models import TaskBase

# todo: change the Path object
console = Console()

CSV_FILE = 'example_posts.csv'
    

def main():
    logging.basicConfig(level=logging.INFO)
    utils.set_openai_api_key()
    df = utils.load_csv(CSV_FILE)
    
    post = df.iloc[0]['text']
    logging.info(f'going the parse the following text:\n {post}')

    task = TaskBase(post=post)
    task.build_prompt()

    console.print("About to send the following prompt🚀", style="#5f5fff")
    print(task.prompt)
    console.print("End of prompt", style="#5f5fff")

    response = utils.get_completion(task.prompt)
    console.print(response)

if __name__ == "__main__":
    main()