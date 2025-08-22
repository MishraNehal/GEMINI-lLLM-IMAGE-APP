# Gemini LLM + Image App (End-to-End)

A minimal end-to-end application that uses **Google Gemini** for both **text** and **image** workflows:
- Chat with an LLM (Gemini 1.5 / 1.0 variants)
- Upload an image and ask questions about it (vision)
- Generate images via Gemini image generation (where supported)
- Clean Streamlit UI, simple backend wrapper, and ready-to-deploy instructions

> Built to mirror the “Building End to End LLM and Large Image Model Application” style project using the **Gemini API**.

## Features

- ✅ Streamlit front end with chat and image Q&A
- ✅ `google-generativeai` SDK for Gemini
- ✅ `.env` based config, no keys hardcoded
- ✅ Reusable `services/gemini_client.py` wrapper
- ✅ Optional image generation endpoint
- ✅ Lightweight tests and pre-commit-style linters (optional)

## Quickstart

1. **Clone & enter**

```bash
git clone YOUR_FORK_URL.git
cd gemini-llm-image-app
```

2. **Create and activate a venv (recommended)**

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set the environment**

Create a `.env` file (or use `export`/`set`) based on `.env.example`:

```bash
cp .env.example .env
```

Then edit `.env` and set:

```
GOOGLE_API_KEY=your_google_generative_ai_key
GEMINI_MODEL=gemini-1.5-pro
IMAGE_MODEL=gemini-1.5-pro
```

5. **Run Streamlit app**

```bash
streamlit run app.py
```

Open the shown local URL in your browser.

## Project Structure

```
gemini-llm-image-app/
├─ app.py                     # Streamlit UI
├─ services/
│  └─ gemini_client.py       # Wrapper around google-generativeai
├─ utils/
│  ├─ env.py                 # Env helpers
│  └─ image_utils.py         # Image helpers
├─ tests/
│  └─ test_smoke.py          # Basic smoke tests
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ README.md
└─ LICENSE
```

## Notes & Tips

- If image generation is unavailable in your region/account/tier, comment the call in the UI or switch to text+vision analysis only.
- You can easily adapt the wrapper to different Gemini model names.
- For deployment, consider Streamlit Community Cloud, Hugging Face Spaces, or Docker.

## License

MIT