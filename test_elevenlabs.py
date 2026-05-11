import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')
print(f"API Key loaded: {api_key[:20]}..." if api_key else "NO API KEY FOUND!")
print(f"Key length: {len(api_key)}" if api_key else "")

# Test the key with a simple API call
url = "https://api.elevenlabs.io/v1/user"
headers = {
    "xi-api-key": api_key
}

print("\nTesting ElevenLabs API key...")
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("✅ API key is valid!")
    data = response.json()
    print(f"Account email: {data.get('xi_api_key', 'N/A')}")
    print(f"Character count: {data.get('character_count', 'N/A')}")
    print(f"Character limit: {data.get('character_limit', 'N/A')}")
elif response.status_code == 401:
    print("❌ API key is INVALID or EXPIRED")
    print(f"Response: {response.text}")
else:
    print(f"Error: {response.status_code}")
    print(f"Response: {response.text}")