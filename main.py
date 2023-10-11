import json
import logging
from json import JSONDecodeError

import pandas as pd
from rich import print
from rich.console import Console

import utils
from models import TaskBase
from loguru import logger
import os

# todo: change the Path object
console = Console()
logger.add("file_{time}.log")

CSV_FILE = "AntiIsraeli.csv"
NUMBER_OF_POSTS = 100
NUMBER_OF_ITERATION_AFTER_ERROR = 2

RESULT_TEXT_FILE = 'result.txt'
RESULT_CSV_FILE = 'result.csv'

def main():
    utils.set_openai_api_key()
    if os.path.exists(RESULT_TEXT_FILE):
        os.remove(RESULT_TEXT_FILE)
    
    df = utils.load_csv(CSV_FILE)
    df = df.sample(NUMBER_OF_POSTS)
    df["text"]=df["text"].fillna("")

    lst = []
    for i, text in enumerate(df["text"].head(NUMBER_OF_POSTS)):
        if text != "":

            logger.info(
            f"------------------- {i} / {NUMBER_OF_POSTS} -------------------------")
            logger.info(f"going the parse the following text:\n {text}")

            task = TaskBase(post=text)
            task.build_prompt()

            for j in range(NUMBER_OF_ITERATION_AFTER_ERROR + 1):

                completion =utils.get_completion(task.prompt)

                try:
                    response = json.loads(completion)
                except JSONDecodeError:
                    logger.error("bad JSON format: %s", completion)
                    continue
                if utils.check_JSON_format(response):
                    response["text"] = text
                    
                    with open(RESULT_TEXT_FILE, 'a', encoding='utf-8') as out_file: 
                        out_file.write(f"{json.dumps(response, ensure_ascii=False)}\n")
                    lst.append(response)
                    
                    break


    res = pd.DataFrame(lst)
    res.to_csv(RESULT_CSV_FILE)


if __name__ == "__main__":
    main()