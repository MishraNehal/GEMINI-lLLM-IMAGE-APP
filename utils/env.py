import os
from dotenv import load_dotenv

def load_env():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY", "")
    text_model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    image_model = os.getenv("IMAGE_MODEL", "gemini-1.5-pro")
    return api_key, text_model, image_model