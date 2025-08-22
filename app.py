import io
import streamlit as st
from PIL import Image

from utils.env import load_env
from utils.image_utils import to_png_bytes
from services.gemini_client import GeminiClient

st.set_page_config(page_title="Gemini LLM + Image App", page_icon="✨", layout="wide")

st.title("✨ Gemini LLM + Image App")
st.caption("Chat with Gemini and ask questions about images.")

with st.sidebar:
    st.header("Configuration")
    api_key, text_model, image_model = load_env()
    st.text_input("GEMINI Text Model", value=text_model, key="text_model")
    st.text_input("GEMINI Image Model", value=image_model, key="image_model")
    if st.button("Initialize Client"):
        if not api_key:
            st.error("Please set GOOGLE_API_KEY in your .env file")
        else:
            st.session_state['client'] = GeminiClient(
                api_key=api_key,
                text_model=st.session_state['text_model'],
                image_model=st.session_state['image_model'],
            )
            st.success("Client initialized.")

tabs = st.tabs(["💬 Chat", "🖼️ Image Q&A", "🎨 Image Generation"])

with tabs[0]:
    st.subheader("Chat with Gemini")
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    for m in st.session_state['messages']:
        with st.chat_message(m['role']):
            st.markdown(m['content'])

    user_input = st.chat_input("Ask me anything...")
    if user_input:
        st.session_state['messages'].append({"role":"user","content":user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        client = st.session_state.get('client')
        if not client:
            st.error("Initialize the client in the sidebar first.")
        else:
            resp = client.chat(st.session_state['messages'])
            st.session_state['messages'].append({"role":"model","content":resp})
            with st.chat_message("model"):
                st.markdown(resp)

with tabs[1]:
    st.subheader("Ask Questions About an Image")
    uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    question = st.text_input("Your question about the image", value="Describe this image")
    if st.button("Analyze Image"):
        if not uploaded:
            st.error("Please upload an image first.")
        else:
            client = st.session_state.get('client')
            if not client:
                st.error("Initialize the client in the sidebar first.")
            else:
                img = Image.open(uploaded).convert("RGB")
                png_bytes = to_png_bytes(img)
                answer = client.ask_about_image(png_bytes, question)
                st.image(img, caption="Uploaded image", use_column_width=True)
                st.markdown("**Answer:**")
                st.write(answer)

with tabs[2]:
    st.subheader("Generate Image from Prompt")
    prompt = st.text_area("Prompt", value="A cozy cabin in the woods, watercolor style")
    if st.button("Generate Image"):
        client = st.session_state.get('client')
        if not client:
            st.error("Initialize the client in the sidebar first.")
        else:
            img_bytes = client.generate_image(prompt)
            if img_bytes:
                st.image(Image.open(io.BytesIO(img_bytes)), use_column_width=True)
            else:
                st.warning("Image generation not available with your current model/tier. Try text+vision in the previous tab.")