import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv('NEWSDATA_API_KEY')
print(f"API Key loaded: {api_key[:10]}..." if api_key else "NO API KEY FOUND!")

url = "https://newsdata.io/api/1/latest"
params = {
    "q": "technology",
    "apikey": api_key,
    "language": "en",
    "country": "us",
    "size": 1,
}

response = requests.get(url, params=params)
print(f"Status: {response.status_code}")
import json; print(json.dumps(response.json(), indent=2))
