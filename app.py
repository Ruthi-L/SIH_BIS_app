import os
import streamlit as st
from retriever import retrieve
from knowledge_base import Chunk
from google import genai

st.set_page_config(page_title="BIS Saarthi Compliance Assistant", layout="centered")

st.markdown("##  BIS Compliance Assistant")
st.markdown("Ask about standards, or paste your product description to check compliance.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your BIS regulatory assistant. Ask me a standard, or paste your product description for a compliance check."
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("Ask about a rule or paste your product description..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 1. Retrieve the most relevant standard
            results = retrieve(user_prompt, top_k=1)
            
            if not results:
                response_text = "I couldn't find a direct standard match for that. Could you tell me a bit more about the specific product or category you're working with?"
            else:
                score, chunk = results[0] # The 'Chunk' object from knowledge_base.py
                
                # 2. Dynamic Conversational Prompt
                chat_prompt = f"""
                You are BIS Saarthi, an expert, warm, and highly personalized regulatory AI collaborator (similar to Gemini). 
                You are talking directly to a manufacturer or entrepreneur.
                
                Retrieved BIS Standard Reference:
                - Standard: {chunk.standard} ({chunk.clause})
                - Rule Details: {chunk.text}
                - Source: {chunk.source}
                
                User's Query/Input: "{user_prompt}"
                
                Instructions:
                - Speak conversationally, engagingly, and directly to the user (e.g., addressing their specific parameters like percentages, product types, or goals).
                - Weave in the official BIS standard naturally to validate their idea or answer their question.
                - If they mention specific metrics (like moisture content), evaluate them directly against the standard limits in a helpful, expert tone.
                - Avoid sounding like a rigid, robotic customer service bot. Be collaborative and insightful.
                """
                
                # 3. Generate response using native google-genai SDK
                api_key = None
                try:
                    if "GOOGLE_API_KEY" in st.secrets:
                        api_key = st.secrets["GOOGLE_API_KEY"]
                except Exception:
                    pass
                    
                if not api_key:
                    api_key = os.getenv("GOOGLE_API_KEY")

                if not api_key:
                    response_text = "Error: GOOGLE_API_KEY not found. Please configure your API key in Streamlit Cloud Secrets."
                else:
                    try:
                        client = genai.Client(api_key=api_key)
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=chat_prompt,
                        )
                        response_text = response.text
                    except Exception as e:
                        # Fallback try with gemini-1.5-flash if 2.5 isn't globally active in their pool yet
                        try:
                            client = genai.Client(api_key=api_key)
                            response = client.models.generate_content(
                                model="gemini-1.5-flash",
                                contents=chat_prompt,
                            )
                            response_text = response.text
                        except Exception as inner_e:
                            response_text = f"An error occurred while generating response: {str(inner_e)}"
            
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})