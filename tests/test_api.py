import requests

# Define the URL and the text to be sent in the POST request
url = "http://localhost:8000/rank"
text = "This is a sample 50-word text. "  # Creating a 50-word text
text2 = "hamas will contrall all the world, you will see"

# Define the data payload as a dictionary with the parameter name "text"
# data = {"text": text, "content_url": "aaaa"}
# data = {"a12": {"text": text, "content_url": "aaaa"}, 'b55': {"text": text2, "content_url": "aaaa"}}
data = {"a12": {"text": text2, "content_url": "aaaa"}}

# Send the POST request
response = requests.post(url, json=data)

# Check the response status code and content
if response.status_code == 200:
    print("Request was successful. Response content:")
    print(response.text)
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.content)
