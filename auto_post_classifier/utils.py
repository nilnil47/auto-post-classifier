import json
import logging
from json import JSONDecodeError
from typing import List

import jsonschema as jsonschema
import openai
import pandas as pd
from loguru import logger
from models import TaskBase

import asyncio
import datetime
import pathlib

from auto_post_classifier.api_request_parallel_processor import process_api_requests


async def create_completion_async(
    user_prompts,
    sys_prompt,
    openai_api_key,
    model="gpt-3.5-turbo-16k",
    output_path="output/responses.txt",
):
    requests = [
        {
            "model": model,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt[0]},
            ],
            "metadata": {"row_id": i, "text": user_prompt[1]},
        }
        for i, user_prompt in enumerate(user_prompts)
    ]

    await process_api_requests(requests, output_path, openai_api_key)


def parse_parallel_responses(responses):
    """Gets a list of responses. outputs 2 lists.
    First - df of the parsing of good responses
    Second - df of bad responses texts"""

    bad_responses_texts = []
    res_list = []
    for completion, text in responses:
        try:
            response = json.loads(completion)
        except JSONDecodeError:
            logger.error(f"bad JSON format: {completion}")
            bad_responses_texts.append(text)
            continue

        if JSON_rank_to_number(response) and check_JSON_format(response):
            response["text"] = text
            response["score"] = generate_score(response)
            res_list.append(response)
        else:
            bad_responses_texts.append(text)
    return res_list, bad_responses_texts


def read_parallel_response(file_path):
    """returns the responses generated by the async completion. returns the data
    in a sorted manner according to the metadata."""

    data = []
    with open(file_path, "r") as file:
        for line in file:
            dictionary_list = json.loads(line)
            if len(dictionary_list) > 2:
                response_dict = dictionary_list[1]
                response_dict["pos"] = int(dictionary_list[2]["row_id"])
                response_dict["text"] = dictionary_list[2]["text"]
                data.append(response_dict)

    # todo do we need sorting?
    # Sort the values by the 'pos' key
    sorted_data = sorted(data, key=lambda x: x["pos"])

    # Extract just the responses of GPT
    return [
        (item["choices"][0]["message"]["content"], item["text"]) for item in sorted_data
    ]


def get_completion(user_prompt, sys_prompt, model="gpt-3.5-turbo-16k"):
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.5,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_completion_chat(user_prompts: List[str], sys_prompt, model="gpt-3.5-turbo-16k"):
    # can be used if we decide to ask the model for each dimension separately.

    messages = [{"role": "system", "content": sys_prompt}]
    responses = []
    for user_prompt in user_prompts:
        messages.append(user_prompt)
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=1,  # this is the degree of randomness of the model's output
        )
        responses.append(response["choices"][0]["message"].content)
        messages.append(
            {"role": "assistant", "content": response["choices"][0]["message"].content}
        )
    return responses


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


def JSON_rank_to_number(response):
    """takes the JSON output and casts the rank to numbers."""
    for key, value in response.items():
        if key.endswith("_rnk") and isinstance(value, str):
            try:
                response[key] = int(value)
            except ValueError:
                return False
    return True


def check_JSON_format(json_data):
    # Define the JSON schema
    schema = {
        "type": "object",
        "properties": {"summary": {"type": "string"}},
        "patternProperties": {
            ".*_exp$": {"type": "string"},
            ".*_rnk$": {"type": "number"},
        },
        "additionalProperties": False,
        "required": ["summary"],
    }

    # Validate the JSON data against the schema
    try:
        jsonschema.validate(instance=json_data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"JSON is not valid: {e.message}")
        return False


def check_JSON_format_no_exp(json_data):
    # Define the JSON schema
    schema = {
        "type": "object",
        "patternProperties": {".*_rnk$": {"type": "number"}},
        "additionalProperties": False,
    }

    # Validate the JSON data against the schema
    try:
        jsonschema.validate(instance=json_data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"JSON is not valid: {e.message}")
        return False


def generate_score_for_df(post: pd.Series):
    """
    Generate score according to GPT rankings if analizing the result by
    loading data frame
    """
    weights = {
        "antisemitism": 0.15,
        "graphic_violence": 0.15,
        "weapons": 0.10,
        "call_for_violence_operation": 0.10,
        "political_content": 0.15,
        "supporting_in_terror": 0.15,
        "misinformation": 0.20,
    }
    score = 0
    for dimension in weights:
        score += post[dimension + "_rnk"] * weights[dimension]

    post["score"] = score
    return post


def generate_score(post: dict):
    """
    Generate score according to GPT rankings while using the app
    """
    weights = {
        "antisemitism": 0.15,
        "graphic_violence": 0.15,
        "weapons": 0.10,
        "endorsement_of_terrorism": 0.10,
        "antiIsrael_extremist": 0.15,
        "calls_for_violence": 0.20,
        "misinformation": 0.20,
    }
    rnk_mtpl_map = {-1.0: -0.2, 0.0: 0.2, 1.0: 1}
    score = 0
    for dimension in weights:
        score += rnk_mtpl_map[post[dimension + "_rnk"]] * weights[dimension]

    return score

async def multiple_posts_loop_asunc(
    openai_api_key: str, posts_dictionary: dict, iter_num: int, base_path:pathlib.Path):
    """asynchronous. Generates gpt responses for all posts in 'posts_enum'.
    returns the results as data frame."""



    response_out_paths = []
    res_list = []
    post_num = len(posts_dictionary)

    for i in range(iter_num):
        user_prompts = []
        sys_prompt = ""  # todo we might want this as a List
        for uuid, text in posts_dictionary.items():
            try:
                if text != "":
                    logger.info(
                        f"------------------- {i} / {post_num} -------------------------"
                    )
                    logger.info(f"going the parse the following text:\n {text}")

                    task = TaskBase(post=text)
                    task.build_prompt()
                    user_prompts.append((task.user_prompt, text))
                    sys_prompt = task.sys_prompt
            except Exception as e:
                logger.error(f"Error while processing post {uuid}: {e}")

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    responses_path = base_path / f"responses_{formatted_datetime}.txt"
    response_out_paths.append(responses_path)
    await create_completion_async(
        user_prompts, sys_prompt, openai_api_key, output_path=responses_path
    )
    res_list, posts_enum = parse_parallel_responses(
        read_parallel_response(responses_path)
    )
            
            
    return res_list
    

