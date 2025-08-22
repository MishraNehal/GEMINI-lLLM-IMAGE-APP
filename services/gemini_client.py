from __future__ import annotations

import io
import os
from typing import List, Optional, Tuple, Union

import google.generativeai as genai
from PIL import Image

class GeminiClient:
    def __init__(self, api_key: str, text_model: str = "gemini-1.5-pro", image_model: str = "gemini-1.5-pro"):
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        genai.configure(api_key=api_key)
        self.text_model_name = text_model
        self.image_model_name = image_model
        self.text_model = genai.GenerativeModel(text_model)
        self.image_model = genai.GenerativeModel(image_model)

    def chat(self, messages: List[dict]) -> str:
        """messages: list of {role: 'user'|'model'|'system', 'content': str}"""
        # Gemini uses 'user'/'model'
        history = [{"role": m.get("role", "user"), "parts": [m.get("content", "")]} for m in messages[:-1]]
        user_msg = messages[-1]["content"] if messages else ""
        chat = self.text_model.start_chat(history=history)
        resp = chat.send_message(user_msg)
        return getattr(resp, "text", str(resp))

    def caption_image(self, image_bytes: bytes, prompt: str = "Describe this image") -> str:
        img = {"mime_type": "image/png", "data": image_bytes}
        resp = self.image_model.generate_content([img, prompt])
        return getattr(resp, "text", str(resp))

    def ask_about_image(self, image_bytes: bytes, question: str) -> str:
        img = {"mime_type": "image/png", "data": image_bytes}
        resp = self.image_model.generate_content([img, question])
        return getattr(resp, "text", str(resp))

    def generate_image(self, prompt: str) -> Optional[bytes]:
        """If your Gemini tier supports image generation via the given model, return PNG bytes; else None."""
        try:
            # Some Gemini endpoints may differ; this is a placeholder for image generation support.
            resp = self.image_model.generate_content([prompt])
            # If the model returns an image part, extract it. Otherwise return None.
            # Many accounts won't have image gen enabled; users can adapt this method to Imagen/other.
            for part in getattr(resp, "candidates", []) or []:
                # Placeholder logic; often Gemini returns text. Adjust per your access.
                pass
            return None
        except Exception:
            return None