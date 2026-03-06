import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

# Ensure the API key is set
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set in the environment variables")

client = genai.Client(api_key=api_key)

print("List of models that support generateContent:\n")
for m in client.models.list():
    for action in m.supported_actions:
        if action == "generateContent":
            print(m.name)

print("List of models that support embedContent:\n")
for m in client.models.list():
    for action in m.supported_actions:
        if action == "embedContent":
            print(m.name)

FREE_TIER_MODELS = {
    # Examples; keep this synced with https://ai.google.dev/gemini-api/docs/pricing
    "models/gemini-2.5-flash",
    "models/gemini-2.5-flash-lite",
    "models/gemini-2.5-pro",
    "models/gemini-3-flash-preview",
    "models/gemini-3.1-flash-lite-preview",
    "models/gemini-embedding-001",
    "models/gemini-2.5-flash-preview-tts",
    "models/gemini-2.5-flash-native-audio-preview-12-2025",
}

print("List of models that are free tier and support generateContent:\n")
for m in client.models.list():
    if m.name in FREE_TIER_MODELS and "generateContent" in m.supported_actions:
        print(m.name)