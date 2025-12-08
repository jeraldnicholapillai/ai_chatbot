import os
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
import faiss
from PyPDF2 import PdfReader
import numpy as np
load_dotenv(override=True)


# -----------------------------
# https://textembedding111.openai.azure.com/openai/deployments/text-embedding-3-small/embeddings?api-version=2023-05-15
# Azure OpenAI Settings
# -----------------------------
endpoint = "https://llmeng.openai.azure.com/"
api_version = "2024-02-15-preview"
api_key = os.getenv('OPENAI_API_KEY')
chat_model = "gpt-4.1-mini"
embed_model = "text-embedding-ada-002"



client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=endpoint,
    api_version=api_version
)

# -----------------------------
# Streamlit Page Setup
# -----------------------------
st.set_page_config(page_title="Jerald RAG Chatbot", layout="centered")
st.title("🧠 Jerald's RAG Chat App (Azure OpenAI)")

# -----------------------------
# FAISS Index + Document Storage
# -----------------------------
if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None

if "documents" not in st.session_state:
    st.session_state.documents = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful RAG assistant."}
    ]


# -----------------------------
# Embed Text (Single Chunk)
# -----------------------------
def embed_text(text):
    """Generate embeddings from Azure OpenAI."""
    response = client.embeddings.create(
        model=embed_model,
        input=[text]     # MUST be a list
    )

    # Convert to numpy array
    vector = np.array(response.data[0].embedding, dtype="float32")

    # Reshape to (1, dim)
    return vector.reshape(1, -1)


# -----------------------------
# Chunking
# -----------------------------
def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]


# -----------------------------
# Process PDF
# -----------------------------
def process_pdf(file):
    pdf = PdfReader(file)
    full_text = ""

    for page in pdf.pages:
        full_text += page.extract_text() + "\n"

    return chunk_text(full_text)


# -----------------------------
# Upload + Index PDF
# -----------------------------
st.subheader("📄 Upload a document for RAG")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    st.info("Processing PDF...")
    chunks = process_pdf(uploaded_file)

    st.info("Generating embeddings & building FAISS index...")

    # Create FAISS Index
    dim = 1536  # embedding dimension for text-embedding-3-small
    index = faiss.IndexFlatL2(dim)

    for chunk in chunks:
        emb = embed_text(chunk)     # THIS NOW RETURNS np.ndarray(1,1536)
        index.add(emb)              # FAISS now works
        st.session_state.documents.append(chunk)

    st.session_state.faiss_index = index
    st.success("Document uploaded & indexed for RAG!")


# -----------------------------
# Retrieve Relevant Chunks
# -----------------------------
def retrieve(query, k=3):
    if st.session_state.faiss_index is None:
        return []

    q_emb = embed_text(query)   # np array (1,1536)
    distances, indices = st.session_state.faiss_index.search(q_emb, k)

    retrieved_chunks = []
    for idx in indices[0]:
        if idx < len(st.session_state.documents):
            retrieved_chunks.append(st.session_state.documents[idx])

    return retrieved_chunks


# -----------------------------
# Display Chat History
# -----------------------------
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# -----------------------------
# User Input
# -----------------------------
user_input = st.chat_input("Ask something...")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Retrieve RAG chunks
    retrieved_chunks = retrieve(user_input)
    rag_context = "\n\n".join(retrieved_chunks)

    prompt = f"""
Use the following context to answer the question. If the answer is not in the context, answer normally.

CONTEXT:
{rag_context}

QUESTION:
{user_input}
"""

    # Call Azure OpenAI Chat Completion
    response = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": "You are a helpful RAG assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    assistant_reply = response.choices[0].message.content

    # Show response
    st.chat_message("assistant").write(assistant_reply)

    # Save to session
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )
