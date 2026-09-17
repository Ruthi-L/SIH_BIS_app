import streamlit as st
from retriever import retrieve
from knowledge_base import Chunk
# Import the new analysis engine
from compliance_engine import analyze_compliance

st.set_page_config(page_title="BIS Saarthi Compliance Assistant", layout="centered")

st.markdown("## 🤖 BIS Saarthi Compliance Assistant")
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

# Helper function to detect if user wants compliance check
def is_compliance_request(text: str):
    keywords = ["check", "product", "item", "my description", "does this meet", "is this compliant"]
    return any(kw in text.lower() for kw in keywords)

if user_prompt := st.chat_input("Ask about a rule or paste your product description..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            # 1. Retrieve the most relevant standard (same as before)
            results = retrieve(user_prompt, top_k=1)
            
            if not results:
                 response_text = "I couldn't find a relevant standard to compare against. Try refining your question."
            else:
                score, chunk = results[0] # The 'Chunk' object from knowledge_base.py
                
                # 2. Check if user prompt implies analysis or just definition
                if is_compliance_request(user_prompt):
                    # Call Gemini for advanced analysis
                    analysis_result = analyze_compliance(chunk, user_prompt)
                    
                    response_text = (
                        f"### 🎯 Compliance Analysis\n"
                        f"**Based on Standard:** {chunk.standard} ({chunk.clause})\n\n"
                        f"{analysis_result}"
                    )
                else:
                    # Fallback to original definition mode
                    response_text = (
                        f"### 📌 Official Rule Statement\n"
                        f"> **{chunk.standard} ({chunk.clause})**\n\n"
                        f"_{chunk.text}_\n\n"
                        f"**Source Reference:** `{chunk.source}`\n\n"
                        f"---\n\n"
                        f"💬 **Here is what that means in plain terms:**\n\n"
                        f"Essentially, when it comes to **{chunk.title.lower()}**, the regulatory framework sets strict boundaries. "
                        f"If you are managing this operation, keeping everything aligned with these provisions ensures complete legal compliance!"
                    )
            
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})