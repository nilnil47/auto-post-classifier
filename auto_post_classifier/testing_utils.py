"""
This script is used to generate a sample request json file
which is needed for the test_main.py testing script
"""
import json
import uuid

import pandas as pd

output_path = "sample.json" # output json path
csv_file = "data/AntiIsraeli.csv" # input csv file 
n = 5 # number of posts to generate in sample.json

df = pd.read_csv(csv_file)
df = df.sample(n=n)

request = {}
for i in range(n):
    post = {
        "text": df.iloc[i]["text"],
        "content_url": df.iloc[i]["content_url"],
    }
    request[uuid.uuid4().hex] = post

print(request)
with open(output_path, "w") as f:
    json.dump(request, f, indent=2)
