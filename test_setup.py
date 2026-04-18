# test_api.py - Now using Groq API
import requests
from dotenv import load_dotenv
import os

# Load your API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {api_key[:10]}..." if api_key else "API Key not found!")

# Send a test message using Groq
try:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": "What is a contract?"}
            ],
            "max_tokens": 500
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print("AI Response:")
        print(result["choices"][0]["message"]["content"])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")