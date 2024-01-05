import json
import os

import pandas as pd
from fastapi.testclient import TestClient

import main
from auto_post_classifier.gpt_handler import GPT_ERROR_REASONS

client = TestClient(main.app)
sample_name = "sample_1.json"
sample_path = f"tests/samples/{sample_name}"
os.environ["MOCK_FILE"] = f"mock/{sample_name}"


def set_up_tests():
    with open(sample_path) as f:
        data = json.load(f)

    request = data["request"]
    number_of_lines_in_sample = len(request)
    volunteers_validation = data["wanted_responses"]

    response = client.post("/rank", json=request)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, dict)

    for uuid, response_entry in response_data.items():
        assert uuid in volunteers_validation, "wrong mock file for the test"
        response_entry["volunteers"] = volunteers_validation[uuid]

    df = pd.DataFrame.from_dict(response_data, orient="index")

    # fixme: fix this
    df.to_csv("test.csv")
    df = pd.read_csv("test.csv")

    return df, number_of_lines_in_sample


df, number_of_lines_in_sample = set_up_tests()


def test_validation():
    assert df.loc[:, "error"].isnull().all()


def test_response_have_all_keys():
    assert len(df) == number_of_lines_in_sample


def test_many_requests_error():
    assert GPT_ERROR_REASONS.TO_MANY_REQUESTS not in df["error"].unique()


def test_json_validation_error():
    assert GPT_ERROR_REASONS.JSON_VALIDARTION not in df["error"].unique()
