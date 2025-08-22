from __future__ import annotations

import time
from typing import List, Optional, Tuple, Union

import google.generativeai as genai
from PIL import Image

class GeminiClient:
    def __init__(self, api_key: str, text_model: str = "gemini-1.5-flash", image_model: str = "gemini-1.5-flash"):
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        genai.configure(api_key=api_key)
        self.text_model_name = text_model
        self.image_model_name = image_model
        self.text_model = genai.GenerativeModel(text_model)
        self.image_model = genai.GenerativeModel(image_model)
        self.max_history_messages = 3
        self.max_tokens = 2000

    def _trim_messages(self, messages: List[dict]) -> List[dict]:
        """Trim messages to stay within token limits and keep only recent history."""
        if len(messages) <= self.max_history_messages:
            return messages
        
        # Keep only the last few messages
        trimmed = messages[-self.max_history_messages:]
        
        # Check token count and trim further if needed
        for i in range(len(trimmed)):
            test_messages = trimmed[i:]
            total_tokens = sum(self.text_model.count_tokens(m.get("content", "")).total_tokens for m in test_messages)
            if total_tokens <= self.max_tokens:
                return test_messages
        
        # If still too long, keep only the last message
        return [trimmed[-1]]

    def _retry_with_backoff(self, func, *args, max_retries=3, **kwargs):
        """Retry function with exponential backoff for rate limiting."""
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        time.sleep(wait_time)
                        continue
                raise e
        return func(*args, **kwargs)  # Final attempt

    def chat(self, messages: List[dict]) -> str:
        """messages: list of {role: 'user'|'model'|'system', 'content': str}"""
        if not messages:
            return ""
        
        # Trim messages for free tier optimization
        trimmed_messages = self._trim_messages(messages)
        
        # Convert to Gemini format
        history = []
        for m in trimmed_messages[:-1]:
            role = m.get("role", "user")
            if role == "model":
                role = "model"  # Gemini uses 'model' for assistant responses
            history.append({"role": role, "parts": [m.get("content", "")]})
        
        user_msg = trimmed_messages[-1]["content"] if trimmed_messages else ""
        
        # Use retry logic for the API call
        def _chat_call():
            chat = self.text_model.start_chat(history=history)
            resp = chat.send_message(user_msg)
            return resp
        
        resp = self._retry_with_backoff(_chat_call)
        return getattr(resp, "text", str(resp))

    def caption_image(self, image_bytes: bytes, prompt: str = "Describe this image") -> str:
        """Caption an image with retry logic."""
        img = {"mime_type": "image/png", "data": image_bytes}
        
        def _caption_call():
            resp = self.image_model.generate_content([img, prompt])
            return resp
        
        resp = self._retry_with_backoff(_caption_call)
        return getattr(resp, "text", str(resp))

    def ask_about_image(self, image_bytes: bytes, question: str) -> str:
        """Ask a question about an image with retry logic."""
        img = {"mime_type": "image/png", "data": image_bytes}
        
        def _image_qa_call():
            resp = self.image_model.generate_content([img, question])
            return resp
        
        resp = self._retry_with_backoff(_image_qa_call)
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