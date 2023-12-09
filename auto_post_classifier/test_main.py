import json

from fastapi.testclient import TestClient

import auto_post_classifier.main as main
import auto_post_classifier.consts as consts
import pandas as pd

client = TestClient(main.app)
sample_path = "../tests/samples/sample_100.json"


def set_up_tests():
    with open(sample_path) as f:
        data = json.load(f)

    request = data["request"]
    volunteers_validation = data["wanted_responses"]

    response = client.post("/rank", json=request)
    assert response.status_code == 200
    response_data = response.json()
    assert type(response.json()) == dict


    for uuid, response_entry in response_data.items():
        response_entry["volunteers"] = volunteers_validation[uuid]
        
    df = pd.DataFrame.from_dict(response_data, orient='index')
    # fixme: fix this
    df.to_csv("test.csv")
    df = pd.read_csv('test.csv')
    return df


df : pd.DataFrame = set_up_tests()


def test_validation():
    # print(df.loc[:, "error"].isnull().all())
    print(df["error"])
    # assert df.loc[:, "error"].isnull().all() == True
    
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


# def _check_validation(response: dict):
#     assert len(response.items()) == 5
#     for uuid, post_response in response.items():
#         assert post_response["error"] == ""
#         _check_correct_astimation(uuid, post_response)
        

# def _check_correct_astimation(post_response, astimation) -> bool:
    
#     pass



# def test_5_pots():
#     with open("sample.json") as f:
#         data = json.load(f)

#     request = data["request"]
#     volunteers_validation = data["wanted_responses"]

#     response = client.post("/rank", json=request)
#     assert response.status_code == 200
#     assert type(response.json()) == dict
#     print(response.json())
#     tests = VolunteersValidation(response.json(), volunteers_validation)
#     tests.df.to_csv("test.csv")

    # _check_validation(response.json())
    # _check_correct_astimation()
