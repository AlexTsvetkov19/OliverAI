import requests
import os
from pprint import pprint

url = "https://api.intelligence.io.solutions/api/v1/models"
# IOINTELLIGENCE_API_KEY= os.getenv("IOINTELLIGENCE_API_KEY")

headers = {
    "accept": "application/json",
    "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjQxN2NhNzM0"
                     "LWEyOGMtNGRiMi04MWEwLWI0OTU5OWJkZWIwMyIsImV4cCI6NDkxMTA3NTMzM30.MD-VC1NPfLk"
                     "iRsG7EH2N-cmXWbzKPev_yrDMu_w5Euo4_5EAY6iLvpE1IgpQPqUWCMyef9UM2l_eB660i6XZfw",
}

response = requests.get(url, headers=headers)
data = response.json()
# pprint(data)

for i in range(len(data['data'])):
    name = data['data'][i]['id']
    print(name)