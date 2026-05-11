import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')
print(f"API Key: {api_key[:20]}...")

# Test actual text-to-speech endpoint
url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": api_key
}

data = {
    "text": "This is a test.",
    "model_id": "eleven_monolingual_v1",
}

print("Testing text-to-speech endpoint...")
response = requests.post(url, json=data, headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("✅ Text-to-speech works! API key is valid for TTS.")
    print(f"Audio size: {len(response.content)} bytes")
elif response.status_code == 401:
    print("❌ Unauthorized - API key invalid for TTS")
    print(f"Response: {response.text}")
else:
    print(f"Error {response.status_code}: {response.text}")