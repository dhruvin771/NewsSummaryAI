import os
import requests
import json
import dotenv
from prompts import system_prompt
dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "gemini-2.5-flash-lite-preview-06-17"

def call_gemini_api(input_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": system_prompt
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": input_text
                    }
                ]
            }
        ],
        "generationConfig": {
            "thinkingConfig": {
                "thinkingBudget": 20000
            },
            "responseMimeType": "application/json"
        }
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    # Extract just the parts content
    if "candidates" in result and len(result["candidates"]) > 0:
        parts = result["candidates"][0]["content"]["parts"]
        if parts and len(parts) > 0:
            return json.loads(parts[0]["text"])
    
    return result

if __name__ == "__main__":
    input_text = "https://www.hindustantimes.com/india-news/nobody-dared-to-touch-him-kolkata-law-student-recounts-monojit-mishras-terror-on-college-campus-101751361544249.html"
    result = call_gemini_api(input_text)
    print(json.dumps(result, indent=2))