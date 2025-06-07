from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from .config import OPENROUTER_API_KEY,OPENROUTER_API_BASE, DEFAULT_LLM_MODEL, EMBEDDING_MODEL

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
    
def get_embedding_model():
    """Initializes and returns a LangChain embedding Ollama client."""
    if not EMBEDDING_MODEL:
        raise ValueError("You must set a local model for embedding. Cannot initialize embedding model.")
    
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL
    )