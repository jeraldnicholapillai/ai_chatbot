import os
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')


# -----------------------------
# 🔐 Azure OpenAI Settings
# -----------------------------
endpoint = "https://llmeng.cognitiveservices.azure.com/"
api_version = "2024-12-01-preview"
api_key = "EZvsLgoMjONIsOjWpZSJj8SVY8DqLtPOktVITBEsG3eyyvxG5kj6JQQJ99BLACF24PCXJ3w3AAAAACOGbtrJ"
deployment = "gpt-4.1-mini"

client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=endpoint,
    api_version=api_version
)

# -----------------------------
# 🌐 Streamlit Page Settings
# -----------------------------
st.set_page_config(page_title="Jerald Chat App", layout="centered")

st.title("💬 Jerald's Chat App (Azure OpenAI)")

# -----------------------------
# 💬 Initialize Session Memory
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# -----------------------------
# 📜 Display chat history
# -----------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# -----------------------------
# ✍️ User Input
# -----------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message
    st.chat_message("user").write(user_input)

    # Save message to memory
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call Azure OpenAI
    response = client.chat.completions.create(
        model=deployment,
        messages=st.session_state.messages,
        temperature=0.7,
        max_tokens=500
    )

    assistant_reply = response.choices[0].message.content

    # Show assistant reply
    st.chat_message("assistant").write(assistant_reply)

    # Save to memory
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )
