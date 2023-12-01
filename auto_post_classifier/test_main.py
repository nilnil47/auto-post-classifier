from fastapi.testclient import TestClient
import json 

import auto_post_classifier.main as main

client = TestClient(main.app)


# def test_config():
#     response = client.get("/config")
#     assert response.status_code == 200
#     assert main.config == response.json()

def test_update_config():
    original_config = client.get("/config")
    assert original_config.status_code == 200
    edited_config = {"test": "test"}
    post_config_response = client.post("/config", json=edited_config)
    assert post_config_response.status_code == 200
    update_config_response = client.get("/config")
    assert update_config_response.status_code == 200
    assert update_config_response.json()["test"] ==  "test"


def _check_validation(response: dict):
    assert len(response.items()) == 5 
    for uuid, post_response in response.items():
        assert post_response["error"] == ""


def test_5_pots():
    with open('sample.json') as f:
        data = json.load(f)
    
    response = client.post("/rank", json=data)
    assert response.status_code == 200
    assert type(response.json()) == dict
    _check_validation(response.json())
