from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
load_dotenv()

groq_api_key = os.getenv(
    "GROQ_API_KEY"
)

llm = ChatGroq(groq_api_key=groq_api_key,model="llama-3.3-70b-versatile")