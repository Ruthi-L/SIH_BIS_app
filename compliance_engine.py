import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from knowledge_base import Chunk
# Initialize the Gemini model (using Gemini 1.5 Flash for speed)
api_key = os.getenv("GOOGLE_API_KEY") # Or st.secrets["GOOGLE_API_KEY"] in Streamlit
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

# Define the system prompt that instructs Gemini on how to act
compliance_system_prompt = """
You are an expert compliance officer for the Bureau of Indian Standards (BIS). 
Your task is to analyze a user's product description against an official BIS standard.

1. **Input:** 
   - Official BIS Standard Clause: {standard_text}
   - User's Product Description: {user_input}

2. **Analysis:** Compare the product description against the requirements mandated in the standard clause. 

3. **Output Requirements:** Provide a clear, structured response:
   - **Conclusion:** State clearly whether the product "Meets" or "Does Not Meet" the standard based *only* on the provided description.
   - **Reasoning:** Explain why, referencing specific points from the standard.
   - **Required Changes:** If it does not meet the standard, provide specific, actionable steps on what needs to change in the product, its specifications, or its labeling to achieve compliance. Be practical and helpful.

Keep your tone professional, authoritative, but helpful to a manufacturer.
"""

def analyze_compliance(retrieved_chunk: Chunk, user_input: str):
    """
    Sends the standard and product description to Gemini for analysis.
    """
    if not api_key:
        return "Error: GOOGLE_API_KEY not found. Please set up your API key to enable compliance analysis."

    prompt = ChatPromptTemplate.from_template(compliance_system_prompt)
    
    # Create the chain linking the prompt and the LLM
    chain = prompt | llm | StrOutputParser()

    # Execute the chain
    result = chain.invoke({
        "standard_text": retrieved_chunk.text,
        "user_input": user_input
    })
    
    return result