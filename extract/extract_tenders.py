import requests
import json

url = 'https://public-api.prozorro.gov.ua/api/2.5/tenders'
params = {"limit": 5}

response = requests.get(url, params=params)
data = response.json()

data_json_formatted = json.dumps(data, indent=4)

print(response.status_code)
print(data_json_formatted)