import logging

import jsonschema as jsonschema
import openai
import pandas as pd


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
        "properties": {".*_exp": {"type": "string"}, ".*_rnk": {"type": "number"}},
        "required": ["summary"],
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
    generate score for according to gpt reankings
    if analizing the result throught loading data frame
    """
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
    """
    generate score for according to gpt reankings
    while using the app
    """
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
        score += float(post[dimension + "_rnk"]) * weights[dimension]
    
    return score