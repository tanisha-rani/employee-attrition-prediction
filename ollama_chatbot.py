import streamlit as st
import requests
from deep_translator import GoogleTranslator

# ========== Configuration ==========
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "phi3"

# ========== Supported Languages ==========
LANGUAGES = {
    "English": "en",
    "Hindi (हिंदी)": "hi",
    "Tamil (தமிழ்)": "ta",
    "Bengali (বাংলা)": "bn",
    "Gujarati (ગુજરાતી)": "gu",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Marathi (मराठी)": "mr",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Telugu (తెలుగు)": "te"
}

# ========== Initialize State ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

if "language" not in st.session_state:
    st.session_state.language = "English"

# ========== Functions ==========
def translate_text(text, source="auto", target="en"):
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception:
        return text  # fallback

# ========== UI ==========
st.title("🌐 Multilingual Chatbot (Ollama + Translation)")
st.markdown("Chat in your own language! Powered by Ollama + Google Translate.")

selected_language = st.selectbox(
    "Choose Language",
    list(LANGUAGES.keys()),
    index=list(LANGUAGES.keys()).index(st.session_state.language)
)
st.session_state.language = selected_language
target_lang_code = LANGUAGES[selected_language]

# Show chat history first
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
user_input = st.chat_input(f"Type your message ({selected_language})")

if user_input:
    # Save and show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Translate to English for Ollama
    translated_input = translate_text(user_input, source=target_lang_code, target="en")

    # Prepare full conversation in English for model
    full_chat = [{"role": "system", "content": "You are a helpful assistant."}]
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            translated = translate_text(msg["content"], source=target_lang_code, target="en")
        else:
            translated = translate_text(msg["content"], source="auto", target="en")
        full_chat.append({"role": msg["role"], "content": translated})

    # Query Ollama
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "messages": full_chat, "stream": False}
        )
        response.raise_for_status()
        data = response.json()
        english_reply = data.get("message", {}).get("content", "No reply from model.")
    except Exception as e:
        english_reply = f"❌ Error: {e}"

    # Translate reply back to chosen language
    final_reply = translate_text(english_reply, source="en", target=target_lang_code)

    # Save + display bot message
    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    with st.chat_message("assistant"):
        st.markdown(final_reply)
