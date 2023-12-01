import json
import uuid

import pandas as pd

output_path = "sample.json"
csv_file = "data/AntiIsraeli.csv"
n = 5

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
