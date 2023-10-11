import json
import logging
from json import JSONDecodeError

import pandas as pd
from rich import print
from rich.console import Console

import utils
from models import TaskBase

# todo: change the Path object
console = Console()

CSV_FILE = "AntiIsraeli.csv"
NUMBER_OF_POSTS = 30


def main():
    logging.basicConfig(level=logging.INFO)
    utils.set_openai_api_key()
    utils.set_private_openai_key()

    df = utils.load_csv(CSV_FILE)
    df["text"]=df["text"].fillna("")

    lst = []
    for i, text in enumerate(df["text"].head(NUMBER_OF_POSTS)):
        logging.info(
            f"------------------- {i} / {NUMBER_OF_POSTS} -------------------------")
        logging.info(f"going the parse the following text:\n {text}")

        task = TaskBase(post=text)
        task.build_prompt()

        console.print("About to send the following prompt🚀", style="#5f5fff")
        print(task.prompt)
        console.print("End of prompt", style="#5f5fff")

        #check for invalid completions, if invalid try again
        while True:
            # todo if loop repeats many times report and break

            completion =utils.get_completion(task.prompt)

            try:
                response = json.loads(completion)
            except JSONDecodeError:
                logging.error("bad JSON format: %s", completion)
                continue
            if utils.check_JSON_format(response):
                response["text"] = text
                lst.append(response)
                break


    res = pd.DataFrame(lst)
    res.to_csv("result.csv")


if __name__ == "__main__":
    main()