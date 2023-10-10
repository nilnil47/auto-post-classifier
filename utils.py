import os

import dotenv
import openai
import pandas as pd


def set_openai_api_key() -> bool:
    """Sets (or make sure that) the OPENAI API key is set
    as an environment variable OPENAI_API_KEY. It will search
    in the following order:
    1. If the environment variable is already set, it will be kept
    2. Next it will search (recursively and upwards) for a .env file
       in the current directory
    3. It will try to read ~/.config/heregpt

    In the last two options, it will look for the key OPENAI_API_KEY.

    Returns
    -------
    bool
        TRUE once the environment variable OPENAI_API_KEY is defined
    """
    if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "":
        return True

    if dotenv.find_dotenv() != "":
        os.environ["OPENAI_API_KEY"] = dotenv.dotenv_values(dotenv.find_dotenv())[
            "OPENAI_API_KEY"
        ]
        if os.getenv("OPENAI_API_KEY") != "":
            return True

    config_file = os.path.expanduser("~/.config/heregpt")
    if os.path.isfile(config_file):
        os.environ["OPENAI_API_KEY"] = dotenv.dotenv_values(config_file)[
            "OPENAI_API_KEY"
        ]
        if os.getenv("OPENAI_API_KEY") != "":
            return True

    return False


def get_completion(prompt, model="gpt-3.5-turbo-16k"):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output

    )
    return response.choices[0].message["content"]

def load_csv(path: str):
    df = pd.read_csv('example_posts.csv')
    return df
