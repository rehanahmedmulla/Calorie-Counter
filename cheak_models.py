import requests
import os
from dotenv import load_dotenv

# API key load karein
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: API Key nahi mili! .env file check karein.")
else:
    print("🔍 Google ke server se models fetch kar rahe hain...\n")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print("✅ AAPKI API KEY KE LIYE YEH MODELS AVAILABLE HAIN:")
        print("-" * 50)
        for model in data.get("models", []):
            # Sirf wahi models dikhayein jo text generate kar sakte hain
            if "generateContent" in model.get("supportedGenerationMethods", []):
                print(f"👉 {model['name']}")
        print("-" * 50)
    else:
        print(f"❌ API Error: {response.text}")