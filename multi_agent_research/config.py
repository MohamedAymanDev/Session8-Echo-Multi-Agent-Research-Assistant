"""config.py - loads environment variables and creates the LLM."""
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Read the .env file (if it exists) into environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def check_api_keys():
    """Return a list with the names of any missing API keys."""
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    return missing


def get_llm():
    """Create the Groq chat model used by all agents."""
    return ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0.3)
