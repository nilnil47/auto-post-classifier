import logging
from typing import List

import jsonschema as jsonschema
import openai
import pandas as pd

from loguru import logger


def get_completion(user_prompt, sys_prompt, model="gpt-3.5-turbo-16k"):
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
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
    responses=[]
    for user_prompt in user_prompts:
        messages.append(user_prompt)
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=1,  # this is the degree of randomness of the model's output
        )
        responses.append(response["choices"][0]["message"].content)
        messages.append(
            {"role": "assistant", "content": response["choices"][0]["message"].content})
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


def check_JSON_format(json_data):
    # Define the JSON schema
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"}
        },
        "patternProperties": {
            ".*_exp$": {"type": "string"},
            ".*_rnk$": {"type": "number"}
        },
        "additionalProperties": False,
        "required": ["summary"]
    }

    # Validate the JSON data against the schema
    try:
        jsonschema.validate(instance=json_data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"JSON is not valid: {e.message}")
        return False

def generate_score_for_df(post: pd.Series):
    weights = {
    "antisemitism": 0.15,
    "graphic_violence": 0.15,
    "weapons": 0.10,
    "call_for_violence_operation": 0.10,
    "political_content": 0.15,
    "supporting_in_terror": 0.15,
    "misinformation": 0.20
}
    score = 0
    for dimension in weights:
        score += post[dimension + "_rnk"] * weights[dimension]
    
    post['score'] = score
    return post

def generate_score(post: dict):
    weights = {
    "antisemitism": 0.15,
    "graphic_violence": 0.15,
    "weapons": 0.10,
    "endorsement_of_terrorism": 0.10,
    "antiIsrael_extremist": 0.15,
    "calls_for_violence": 0.20,
    "misinformation": 0.20
}
    rnk_mtpl_map = {-1.0: -0.5, 0.0: 0.2, 1.0: 1}
    score = 0
    for dimension in weights:
        score += rnk_mtpl_map[float(post[dimension + "_rnk"])] * weights[dimension]
    
    return score