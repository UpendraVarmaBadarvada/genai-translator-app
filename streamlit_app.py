# app.py

import streamlit as st
from gtts import gTTS
import openai
import tempfile
import os
import pandas as pd
import fitz  # PyMuPDF

# --- SETUP ---

st.set_page_config(page_title="GenAI Translator", layout="centered")
st.title("🌍 GenAI Text Translator & Speech Generator")

# --- API Key Input ---
api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

# --- LANGUAGE SELECTION ---
languages = {
    "French": "fr",
    "Spanish": "es",
    "Hindi": "hi",
    "German": "de",
    "Italian": "it",
    "Chinese": "zh",
    "Arabic": "ar",
    "Japanese": "ja"
}
target_language = st.selectbox("🌐 Select a target language", list(languages.keys()))

# --- TEXT INPUT AREA ---
st.markdown("#### ✏️ Enter Text or Upload a File")
user_text = st.text_area("Write or paste your text here", height=150)

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Or upload a file (.txt, .pdf, .csv, .xlsx)", type=["txt", "pdf", "csv", "xlsx"])

def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.name.endswith(".pdf"):
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                return "\n".join(page.get_text() for page in doc)
        elif uploaded_file.name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            return df.to_string(index=False)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            return df.to_string(index=False)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""

if uploaded_file and not user_text:
    user_text = extract_text_from_file(uploaded_file)
    st.success("✅ Text extracted from uploaded file!")

# --- TRANSLATE FUNCTION ---
def translate_text(text, target_language, api_key):
    openai.api_key = api_key
    prompt = f"Translate this to {target_language}:\n\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"❌ Translation failed: {e}")
        return None

# --- TTS FUNCTION ---
def generate_audio(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.error(f"❌ Audio generation failed: {e}")
        return None

# --- TRANSLATE BUTTON ---
if st.button("🔄 Translate"):
    if not api_key:
        st.warning("Please enter your OpenAI API key.")
    elif not user_text:
        st.warning("Please provide some text or upload a file.")
    else:
        translated_text = translate_text(user_text, target_language, api_key)
        if translated_text:
            st.markdown("### ✅ Translated Text")
            st.text_area("Translation Output", value=translated_text, height=150)
            
            # --- TEXT TO SPEECH ---
            if st.button("🔊 Convert to Speech"):
                audio_file_path = generate_audio(translated_text, languages[target_language])
                if audio_file_path:
                    st.audio(audio_file_path, format="audio/mp3")
                    with open(audio_file_path, "rb") as f:
                        st.download_button("⬇️ Download Audio", f, file_name="translated_audio.mp3")
