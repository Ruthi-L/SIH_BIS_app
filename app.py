import os
import time
import streamlit as st
from retriever import retrieve
from knowledge_base import Chunk
from google import genai
from google.genai import types

st.set_page_config(page_title="BIS Saarthi Compliance Assistant", layout="centered")

st.markdown("## BIS Compliance Assistant")
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
            # 1. Retrieve the most relevant standard from your knowledge base
            results = retrieve(user_prompt, top_k=1)
            
            if not results:
                response_text = "I couldn't find a direct standard match for that. Could you tell me a bit more about the specific product or category you're working with?"
            else:
                score, chunk = results[0]
                
                # 2. Build the conversational Gemini prompt with structured rule-first requirement
                chat_prompt = f"""
                You are BIS Saarthi, an expert, and highly personalized regulatory AI collaborator (similar to Gemini). 
                You are talking directly to a manufacturer or entrepreneur.
                
                Retrieved BIS Standard Reference:
                - Standard Name: {chunk.standard}
                - Clause / Section Number: {chunk.clause}
                - Rule Details: {chunk.text}
                - Source Reference: {chunk.source}
                
                User's Query/Input: "{user_prompt}"
                
                Instructions:
                - Structure your response cleanly:
                  1. **Official Standard Reference:** Clearly state the standard name, clause/section number, and official rule text right at the beginning before any conversation.
                  2. **Personalized Analysis:** Follow up immediately in a brief engaging tone. Do not include any greetings. Address the user's specific parameters (like moisture percentages, product types, product materials, startup goals, or queries regarding rules and regulations) directly against the rule.
                  3. **Actionable Advice:** Provide clear, actionable advice or next steps for the user, ensuring you keep it relevant to their specific query.
                - Keep the response punchy, concise, and focused to ensure fast generation times.
                """
                
                # 3. Fetch API key and generate response via direct Google GenAI SDK with speed configs
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
                    response_text = None
                    client = genai.Client(api_key=api_key)
                    
                    # Add generation config to restrict token length for faster output
                    config = types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=600,
                    )
                    
                    for attempt in range(3):
                        try:
                            response = client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=chat_prompt,
                                config=config
                            )
                            response_text = response.text
                            break
                        except Exception as e:
                            if ("503" in str(e) or "UNAVAILABLE" in str(e)) and attempt < 2:
                                time.sleep(1.0)
                                continue
                            else:
                                response_text = f"An error occurred while generating response: {str(e)}"
            
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})