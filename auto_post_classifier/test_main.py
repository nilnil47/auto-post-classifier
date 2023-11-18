from fastapi.testclient import TestClient
import json 

import auto_post_classifier.main as main

client = TestClient(main.app)


def test_config():
    response = client.get("/config")
    assert response.status_code == 200
    assert main.config == response.json()

# def test_5_pots():
#     with open('sample.json') as f:
#         data = json.load(f)
    
#     response = client.post("/rank", json=data)
#     assert response.json == {}
    