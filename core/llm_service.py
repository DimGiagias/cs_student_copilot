from langchain_openai import ChatOpenAI
from .config import OPENROUTER_API_KEY,OPENROUTER_API_BASE, DEFAULT_LLM_MODEL

def get_llm(model_name: str = DEFAULT_LLM_MODEL, temperature: float = 0.1):
    """Initializes and returns a LangChain LLM client configured for OpenRouter."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set. Cannot initialize LLM.")

    return ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        openai_api_base=OPENROUTER_API_BASE,
        openai_api_key=OPENROUTER_API_KEY,
    )