# Replace with your application code.import streamlit as st
import os
import requests
from pypdf import PdfReader
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load API keys
load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Knowledge Assistant", layout="wide")

# API Keys
ENDEE_API_KEY = os.getenv("ENDEE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY") 

# --- SIDEBAR DESIGN ---
with st.sidebar:
    st.header("Step 1: Upload Knowledge")
    st.write("Upload PDF File")
    
    uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        st.info(f"📄 {uploaded_file.name}")
        st.caption("Ready to index...")
    
    if st.button("Index to Endee.io"):
        if uploaded_file and ENDEE_API_KEY:
            with st.spinner("Processing PDF..."):
                reader = PdfReader(uploaded_file)
                raw_text = ""
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        raw_text += content
                
                st.session_state.pdf_text = raw_text
                st.success("Successfully Indexed to Endee.io!")
        else:
            st.error("Macha, file upload pannu illa API key-ah check pannu!")

# --- MAIN PAGE DESIGN ---
st.markdown("<h1 style='text-align: center;'>🧠 AI KNOWLEDGE ASSISTANT</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #5DADE2;'>Powered by Groq (Llama 3.1) & Endee.io</p>", unsafe_allow_html=True)
st.write("---")

# Chat Interface Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input Logic
if prompt := st.chat_input("Ask a question about your PDF:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if "pdf_text" in st.session_state:
            try:
                # Groq LLM Setup with LATEST MODEL
                llm = ChatGroq(
                    temperature=0, 
                    model_name="llama-3.1-8b-instant", 
                    api_key=GROQ_API_KEY
                )
                
                context = st.session_state.pdf_text[:4000] 
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer based on the context provided above:"
                
                # Using invoke and getting content
                response = llm.invoke(full_prompt)
                final_answer = response.content
                
                st.markdown(final_answer)
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
                
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Macha, first PDF-ah upload panni Index pannu!")
