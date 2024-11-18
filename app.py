from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import sys
from main import create_response


load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
with st.sidebar:
    st.markdown(
    """
    <div style="text-align: center;">
        <img src="assets/images/icon.webp" width="100">
        <h1>CHATBOT AKADEMIK UNDIKSHA (AKASHA)</h1>
    </div>
    """,
    unsafe_allow_html=True
)
st.title("👨‍🦰 Yuk Tanya Akasha")
st.caption("🚀 Chatbot Informasi Akademik Undiksha")

# Inisialisasi session state untuk menyimpan pesan
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Menampilkan pesan yang sudah ada di chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Input dari user
if prompt := st.chat_input():
    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Menampilkan spinner sebagai animasi loading
    with st.spinner('Akasha sedang mengetik...'):
        response = create_response(prompt)
        # response = chat_groq(prompt)
    
    # Menyimpan pesan assistant ke dalam session state
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Menampilkan pesan dari assistant
    st.chat_message("assistant").write(response)
