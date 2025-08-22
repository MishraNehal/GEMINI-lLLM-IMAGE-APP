import io
import json
import streamlit as st
from PIL import Image
from datetime import datetime

from utils.env import load_env
from utils.image_utils import to_png_bytes
from services.gemini_client import GeminiClient

st.set_page_config(page_title="Gemini LLM + Image App", page_icon="🤖", layout="wide")

# Modern, professional styling without colors
st.markdown("""
<style>
    /* Professional typography */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
        letter-spacing: -0.02em;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 2rem;
        opacity: 0.8;
        font-weight: 400;
    }
    
    /* Enhanced spacing and layout */
    .stApp {
        padding: 2rem 1rem;
    }
    
    /* Professional sidebar */
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-color: #d0d0d0;
    }
    
    /* Enhanced input fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #f0f0f0;
        transition: all 0.2s ease;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #666;
        box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
    }
    
    /* Enhanced file uploader */
    .stFileUploader > div > div {
        border-radius: 8px;
        border: 2px dashed #e0e0e0;
        background: #fafafa;
        transition: all 0.2s ease;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #ccc;
        background: #f5f5f5;
    }
    
    /* Professional tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 1rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: #f8f9fa;
        border-bottom: 3px solid #666;
    }
    
    /* Enhanced chat messages */
    .stChatMessage {
        border-radius: 12px;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    
    /* Professional spacing */
    .stMarkdown {
        margin: 1rem 0;
    }
    
    /* Smooth animations */
    * {
        transition: all 0.2s ease;
    }
    
    /* Enhanced headers */
    h1, h2, h3 {
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Better form spacing */
    .stForm {
        padding: 1.5rem;
        border-radius: 12px;
        background: #fafafa;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Conversation history management functions
def save_conversation(messages, title=None):
    """Save conversation to session state and local storage"""
    if not title:
        title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    conversation = {
        "title": title,
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }
    
    if 'saved_conversations' not in st.session_state:
        st.session_state['saved_conversations'] = []
    
    st.session_state['saved_conversations'].append(conversation)
    return title

def load_conversation(conversation):
    """Load a saved conversation"""
    st.session_state['messages'] = conversation['messages']
    st.success(f"Loaded conversation: {conversation['title']}")

def delete_conversation(index):
    """Delete a saved conversation"""
    if 'saved_conversations' in st.session_state:
        deleted = st.session_state['saved_conversations'].pop(index)
        st.success(f"Deleted conversation: {deleted['title']}")

# Professional header with enhanced typography
st.markdown('<h1 class="main-title">Gemini LLM + Image App</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Advanced AI-powered chat and image analysis platform</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    ">
        <h3 style="margin: 0 0 1rem 0; text-align: center; font-weight: 600;">Configuration</h3>
        <p style="margin: 0; text-align: center; font-size: 0.9rem; color: #6c757d; line-height: 1.4;">
            <strong>App Features:</strong><br>
            • AI Chat with Gemini<br>
            • Image Analysis & Q&A<br>
            • Image Generation<br>
            • Conversation History<br>
            • Multi-model Support<br>
            • Free Tier Optimized
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    api_key, text_model, image_model = load_env()
    
    st.markdown("**Text Model**")
    st.text_input("", value=text_model, key="text_model", label_visibility="collapsed")
    
    st.markdown("**Image Model**")
    st.text_input("", value=image_model, key="image_model", label_visibility="collapsed")
    
    st.markdown("---")
    
    if st.button("Initialize Client", use_container_width=True):
        if not api_key:
            st.error("Please set GOOGLE_API_KEY in your .env file")
        else:
            st.session_state['client'] = GeminiClient(
                api_key=api_key,
                text_model=st.session_state['text_model'],
                image_model=st.session_state['image_model'],
            )
            st.success("Client initialized successfully!")

tabs = st.tabs(["Chat", "Image Analysis", "Image Generation", "Conversation History"])

with tabs[0]:
    st.markdown("""
    <div style="
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    ">
        <h3 style="margin: 0 0 1.5rem 0; color: #495057;">Chat with Gemini</h3>
    """, unsafe_allow_html=True)
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    
    # Chat container with better styling
    chat_container = st.container()
    with chat_container:
        for m in st.session_state['messages']:
            with st.chat_message(m['role']):
                st.markdown(m['content'])

    user_input = st.chat_input("Type your message here...")
    if user_input:
        st.session_state['messages'].append({"role":"user","content":user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        client = st.session_state.get('client')
        if not client:
            st.error("Please initialize the client in the sidebar first.")
        else:
            with st.spinner("Gemini is thinking..."):
                resp = client.chat(st.session_state['messages'])
                st.session_state['messages'].append({"role":"model","content":resp})
            
            # Rerun to show new messages
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    st.markdown("""
    <div style="
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    ">
        <h3 style="margin: 0 0 1.5rem 0; color: #495057;">Image Analysis</h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Upload Image**")
        uploaded = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        
        if uploaded:
            img = Image.open(uploaded).convert("RGB")
            st.image(img, caption="Uploaded Image", use_column_width=True)
    
    with col2:
        st.markdown("**Ask Questions**")
        question = st.text_input("Question about the image", value="Describe this image in detail")
        
        if st.button("Analyze Image", use_container_width=True):
            if not uploaded:
                st.error("Please upload an image first.")
            else:
                client = st.session_state.get('client')
                if not client:
                    st.error("Please initialize the client in the sidebar first.")
                else:
                    with st.spinner("Analyzing image..."):
                        png_bytes = to_png_bytes(img)
                        answer = client.ask_about_image(png_bytes, question)
                    
                    st.markdown("**Analysis Result:**")
                    st.info(answer)
    
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown("""
    <div style="
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    ">
        <h3 style="margin: 0 0 1.5rem 0; color: #495057;">Image Generation</h3>
    """, unsafe_allow_html=True)
    
    st.markdown("**Describe the image you want to generate:**")
    prompt = st.text_area("", value="A modern minimalist office space with natural lighting, clean lines, and plants", 
                          height=100, label_visibility="collapsed", 
                          placeholder="Describe your image in detail...")
    
    if st.button("Generate Image", use_container_width=True):
        client = st.session_state.get('client')
        if not client:
            st.error("Please initialize the client in the sidebar first.")
        else:
            with st.spinner("Generating image..."):
                img_bytes = client.generate_image(prompt)
            
            if img_bytes:
                st.success("Image generated successfully!")
                st.image(Image.open(io.BytesIO(img_bytes)), use_column_width=True)
            else:
                st.info("Image generation is not available with your current model or account tier. You can still use the Image Analysis tab for analyzing uploaded images.")
    
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[3]:
    st.markdown("""
    <div style="
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    ">
        <h3 style="margin: 0 0 1.5rem 0; color: #495057;">Conversation History</h3>
    """, unsafe_allow_html=True)
    
    # Save current conversation
    if 'messages' in st.session_state and st.session_state['messages']:
        col1, col2 = st.columns([3, 1])
        with col1:
            save_title = st.text_input("Conversation Title (optional)", 
                                     value=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        with col2:
            if st.button("Save Conversation", use_container_width=True):
                title = save_conversation(st.session_state['messages'], save_title)
                st.success(f"Saved: {title}")
    
    st.markdown("---")
    
    # Display saved conversations
    if 'saved_conversations' in st.session_state and st.session_state['saved_conversations']:
        st.markdown("**Saved Conversations:**")
        
        for i, conv in enumerate(st.session_state['saved_conversations']):
            with st.expander(f"📁 {conv['title']} - {conv['timestamp'][:16]}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**Messages:** {len(conv['messages'])}")
                    st.markdown(f"**Created:** {conv['timestamp'][:16]}")
                
                with col2:
                    if st.button("Load", key=f"load_{i}", use_container_width=True):
                        load_conversation(conv)
                
                with col3:
                    if st.button("Delete", key=f"delete_{i}", use_container_width=True):
                        delete_conversation(i)
                        st.rerun()
                
                # Show conversation preview
                st.markdown("**Preview:**")
                for msg in conv['messages'][:3]:  # Show first 3 messages
                    role = "You" if msg['role'] == 'user' else "Gemini"
                    st.markdown(f"**{role}:** {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
                
                if len(conv['messages']) > 3:
                    st.markdown(f"*... and {len(conv['messages']) - 3} more messages*")
    else:
        st.info("No saved conversations yet. Start chatting to save your conversations!")
    
    st.markdown("</div>", unsafe_allow_html=True)