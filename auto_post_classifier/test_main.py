import json
import os

import pandas as pd
from fastapi.testclient import TestClient

import auto_post_classifier.main as main

client = TestClient(main.app)
# sample_path = "../tests/samples/sample_100.json"
sample_name = "sample_100.json"
sample_path = f"../tests/samples/{sample_name}"
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
    assert df.loc[:, "error"].isnull().all() is True
