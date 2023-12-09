"""
This script is used to generate a sample request json file
which is needed for the test_main.py testing script
"""
import json

import pandas as pd

output_path = "sample.json"  # output json path
csv_file = "../data/data_classified.csv"  # input csv file
n = 1  # number of posts to generate in sample.json

df = pd.read_csv(csv_file)
df = df.sample(n=n)

request = {}
wanted_responses = {}

for i in range(n):
    id = df.iloc[i]["Id"]
    post = {
        "text": df.iloc[i]["Content"],
        "content_url": df.iloc[i]["Url"],
    }
    request[id] = post
    wanted_responses[id] = df.iloc[i]["Category"]

sample_json = {
    "request": request,
    "wanted_responses": wanted_responses,
}

with open(output_path, "w") as f:
    json.dump(sample_json, f, indent=2)
