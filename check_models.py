import os
from dotenv import load_dotenv
import google.generativeai as genai

# ==========================================================
# 1️⃣ Load Environment Variables
# ==========================================================
print("🔍 Loading .env file...")
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file!")
    print("👉 Please add it like this:\nGOOGLE_API_KEY=gen-lang-client-XXXXXXXXXXXX")
    exit(1)
else:
    print(f"✅ API key loaded successfully: {api_key[:15]}********")

# ==========================================================
# 2️⃣ Configure Google Generative AI
# ==========================================================
try:
    genai.configure(api_key=api_key)
    print("⚙️  Configured Google Generative AI client successfully.")
except Exception as e:
    print(f"❌ Failed to configure API key: {e}")
    exit(1)

# ==========================================================
# 3️⃣ Display Available Models
# ==========================================================
print("\n📋 Fetching available models...\n")

try:
    models = list(genai.list_models())

    if not models:
        print("⚠️ No models found. Check if your API key has Generative AI access.")
    else:
        for i, model in enumerate(models, start=1):
            print(f"{i}. {model.name}")

        print("\n✅ Models fetched successfully!")
        print("💡 Example: Use 'gemini-2.5-pro' or 'gemini-2.5-flash' in your checker.py")

except Exception as e:
    print(f"❌ ERROR: Unable to list models.\nDetails: {e}")
