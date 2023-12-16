import json
import os

import pandas as pd
from fastapi.testclient import TestClient

import auto_post_classifier.main as main

from .gpt_handler import GPT_ERROR_REASONS

client = TestClient(main.app)
# sample_path = "../tests/samples/sample_100.json"
sample_name = "sample_100.json"
sample_path = f"../tests/samples/{sample_name}"
number_of_lines_in_sample = 100
os.environ["MOCK_FILE"] = f"../mock/{sample_name}"


def set_up_tests():
    with open(sample_path) as f:
        data = json.load(f)

    request = data["request"]
    volunteers_validation = data["wanted_responses"]

    response = client.post("/rank", json=request)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, dict)

    for uuid, response_entry in response_data.items():
        response_entry["volunteers"] = volunteers_validation[uuid]

    df = pd.DataFrame.from_dict(response_data, orient="index")

    # fixme: fix this
    df.to_csv("test.csv")
    df = pd.read_csv("test.csv")

    return df


df: pd.DataFrame = set_up_tests()


def test_validation():
    assert df.loc[:, "error"].isnull().all()


def test_response_have_all_keys():
    assert len(df) == number_of_lines_in_sample


def test_many_requests_error():
    assert not GPT_ERROR_REASONS.TO_MANY_REQUESTS in df["error"].unique()


def test_json_validation_error():
    assert not GPT_ERROR_REASONS.JSON_VALIDARTION in df["error"].unique()
