import requests
from pprint import pprint


url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjQxN"
                     "2NhNzM0LWEyOGMtNGRiMi04MWEwLWI0OTU5OWJkZWIwMyIsImV4cCI6NDkxMTA3NTMzM"
                     "30.MD-VC1NPfLkiRsG7EH2N-cmXWbzKPev_yrDMu_w5Euo4_5EAY6iLvpE1IgpQPqUWCMyef9UM2l_eB660i6XZfw"
}

data = {
    "model": "deepseek-ai/DeepSeek-R1-0528",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "how are you doing"
        }
    ]
}

response = requests.post(url, headers=headers, json=data)
data = response.json()
pprint(data)

# text = data['choices'][0]['message']['content']
# print(text.split('</think>\n')[1])