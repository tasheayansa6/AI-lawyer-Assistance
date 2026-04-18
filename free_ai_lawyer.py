import streamlit as st
import requests
import json
from typing import Optional

# Free AI Options
class FreeAIService:
    def __init__(self):
        self.services = {
            "HuggingFace (Free)": self.huggingface_chat,
            "Groq (Free Tier)": self.groq_chat,
            "Local Ollama": self.ollama_chat
        }
    
    def huggingface_chat(self, message: str, model: str = "microsoft/DialoGPT-medium") -> str:
        """Free HuggingFace inference API"""
        try:
            API_URL = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": "Bearer hf_dummy"}  # Public models don't need auth
            payload = {"inputs": message}
            
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "I'm here to help with legal questions.")
            return "Service temporarily unavailable. Try another option."
        except:
            return "HuggingFace service error. Please try another option."
    
    def groq_chat(self, message: str) -> str:
        """Groq API - Free tier available"""
        try:
            # Load actual API key
            from dotenv import load_dotenv
            import os
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            
            API_URL = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a helpful legal assistant. Provide general legal information but always recommend consulting a qualified attorney for specific legal advice."},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 500
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            return "Groq service temporarily unavailable."
        except:
            return "Groq service error. Please try another option."
    
    def ollama_chat(self, message: str) -> str:
        """Local Ollama service (if installed)"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",  # or "mistral", "codellama"
                    "prompt": f"As a legal assistant, please help with: {message}",
                    "stream": False
                },
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("response", "Ollama response error.")
            return "Ollama not running. Install from ollama.com and run 'ollama serve'"
        except:
            return "Ollama not available. Install from ollama.com and run 'ollama serve'"

def main():
    st.set_page_config(
        page_title="AI Legal Assistant",
        page_icon=" scales",
        layout="wide"
    )
    
    st.title(" scales AI Legal Assistant")
    st.markdown("*Free AI-powered legal information assistance*")
    
    # Disclaimer
    st.warning(" DISCLAIMER: This AI provides general legal information only. It's not a substitute for professional legal advice. Always consult with a qualified attorney for specific legal matters.")
    
    # Initialize AI service
    ai_service = FreeAIService()
    
    # Service selection
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_service = st.selectbox(
            "Choose AI Service:",
            list(ai_service.services.keys()),
            index=0
        )
    
    with col2:
        if st.button("Check Service Status"):
            with st.spinner("Testing service..."):
                test_response = ai_service.services[selected_service]("Hello, are you working?")
                st.info(f"Service response: {test_response[:100]}...")
    
    # Chat interface
    st.subheader("Ask Your Legal Question")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    if prompt := st.chat_input("Type your legal question here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner(f"Thinking using {selected_service}..."):
                response = ai_service.services[selected_service](prompt)
                st.markdown(response)
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sidebar with legal resources
    with st.sidebar:
        st.header("Legal Resources")
        st.markdown("""
        **Free Legal Aid:**
        - [Legal Services Corporation](https://www.lsc.gov/)
        - [LawHelp.org](https://www.lawhelp.org/)
        - [FindLegalHelp.org](https://findlegalhelp.org/)
        
        **Common Legal Topics:**
        - Contract Law
        - Family Law  
        - Landlord/Tenant Issues
        - Employment Law
        - Small Claims Court
        """)
        
        st.header("Installation Instructions")
        st.markdown("""
        **For Ollama (Local AI):**
        1. Visit [ollama.com](https://ollama.com)
        2. Download and install
        3. Run: `ollama serve`
        4. Install model: `ollama pull llama3.2`
        
        **For Groq:**
        1. Sign up at [groq.com](https://groq.com)
        2. Get free API key
        3. Replace "gsk_demo" with your key
        """)

if __name__ == "__main__":
    main()
