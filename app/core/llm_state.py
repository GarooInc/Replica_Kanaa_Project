# app/core/llm_state.py

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

LLM = ChatOpenAI(
    model="gpt-4o",
    temperature=0.5,
    streaming=True,
    max_retries=3
)

TOOLS = None
