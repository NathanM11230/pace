import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv('NEWS_API_KEY')
print(f"API Key loaded: {api_key[:10]}..." if api_key else "NO API KEY FOUND!")

url = "https://newsapi.org/v2/everything"
params = {
    "q": "technology",
    "apiKey": api_key,
    "language": "en",
    "pageSize": 1
}

response = requests.get(url, params=params)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")