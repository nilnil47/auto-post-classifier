import logging
import os
import re

import dotenv
import jsonschema as jsonschema
import openai
import pandas as pd

QUOTE_REPLACE = '@QUOTE@'

# todo remove
def set_private_openai_key():
    openai.api_key = input("Please enter your OpenAi API key: ")


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
        openai.api_key=dotenv.dotenv_values(dotenv.find_dotenv())[
            "OPENAI_API_KEY"
        ]
        if os.getenv("OPENAI_API_KEY") != "":
            return True

    config_file = os.path.expanduser("~/.config/heregpt")
    if os.path.isfile(config_file):
        os.environ["OPENAI_API_KEY"] = dotenv.dotenv_values(config_file)[
            "OPENAI_API_KEY"
        ]
        openai.api_key = dotenv.dotenv_values(config_file)[
            "OPENAI_API_KEY"
        ]
        if os.getenv("OPENAI_API_KEY") != "":
            return True

    return False


def get_completion(prompt, model="gpt-3.5-turbo-16k"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=1,  # this is the degree of randomness of the model's output

    )
    return response.choices[0].message["content"]


def transcribe(audio_path):
    # File uploads are currently limited to 25 MB and the following input file
    # types are supported: mp3, mp4, mpeg, mpga, m4a, wav, and webm.

    audio_file = open(audio_path, "rb")
    # we might want to use translate (which outputs an english translation).
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript


def load_csv(path: str):
    df = pd.read_csv(path)
    return df


def check_JSON_format(json_data):
    # Define the JSON schema
    schema = {
        "type": "object",
        "properties": {
            ".*_exp": {"type": "string"},
            ".*_rnk": {"type": "number"}
        },
        "required": ["summary"]
    }

    # Validate the JSON data against the schema
    try:
        jsonschema.validate(instance=json_data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"JSON is not valid: {e.message}")
        return False

    # json = json.replace('"', QUOTE_REPLACE)
    #
    # pattern = r"\{((?:\s*\"(?:(?!\").)+_exp\":\s*\"(?:(?!\").)+\"\s*,\s*\"(?:(?!\").)+_rnk\":\s*-?\d\s*,\s*)*)\"summary\":\s*\"(?:(?!\").)+\"\s*\}"
    # pattern  = pattern.replace("\"", QUOTE_REPLACE)
    # match = re.search(pattern, json)
    # return bool(match)
    #