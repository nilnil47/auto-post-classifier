import json

from fastapi.testclient import TestClient

import auto_post_classifier.main as main
import auto_post_classifier.consts as consts
import pandas as pd

client = TestClient(main.app)

def set_up_tests():
    with open("sample.json") as f:
        data = json.load(f)

    request = data["request"]
    volunteers_validation = data["wanted_responses"]

    response = client.post("/rank", json=request)
    assert response.status_code == 200
    assert type(response.json()) == dict
    print(response.json())
    tests = VolunteersValidation(response.json(), volunteers_validation)
    tests.df.to_csv("test.csv")
    return tests

class VolunteersValidation:
    def __init__(self, response: dict, volunteers_classification: dict) -> None:
        for uuid, response_entry in response.items():
            response_entry["volunteers"] = volunteers_classification[uuid]
        
        df = pd.DataFrame.from_dict(response, orient='index')
        # todo: delete the first colum
        self.df = df

        
    @staticmethod
    def classic_antisemitism(response):
        response["antisemitism_rnk"] == 1

    @staticmethod
    def pro_palestine(response):
        return True
    
    @staticmethod
    def not_harmful(response):
        df = pd.DataFrame(response)
        df = df.loc[:, df.columns.str.startswith('_rnk')]
        return True 

tests : VolunteersValidation = set_up_tests()

def test_validation():
    
# volunteers_validation_options = {
#     "ClassicAntisemitism": lambda response: response["antisemitism_rnk"] == 1,
#     "ProPalestine": lambda response: response["antisemitism_rnk"] == 1,
#     "NonHarmful": lambda response: response["antisemitism_rnk"] == 1 ,
#     "ProHamas",
#     "AntiIsraeli",
#     "Holocaust"
# }

# def test_config():
#     response = client.get("/config")
#     assert response.status_code == 200
#     assert main.config == response.json()


# def test_update_config():
#     original_config = client.get("/config")
#     assert original_config.status_code == 200
#     edited_config = {"test": "test"}
#     post_config_response = client.post("/config", json=edited_config)
#     assert post_config_response.status_code == 200
#     update_config_response = client.get("/config")
#     assert update_config_response.status_code == 200
#     assert update_config_response.json()["test"] == "test"


def _check_validation(response: dict):
    assert len(response.items()) == 5
    for uuid, post_response in response.items():
        assert post_response["error"] == ""
        _check_correct_astimation(uuid, post_response)
        

def _check_correct_astimation(post_response, astimation) -> bool:
    
    pass



def test_5_pots():
    with open("sample.json") as f:
        data = json.load(f)

    request = data["request"]
    volunteers_validation = data["wanted_responses"]

    response = client.post("/rank", json=request)
    assert response.status_code == 200
    assert type(response.json()) == dict
    print(response.json())
    tests = VolunteersValidation(response.json(), volunteers_validation)
    tests.df.to_csv("test.csv")

    # _check_validation(response.json())
    # _check_correct_astimation()
