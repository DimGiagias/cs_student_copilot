import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not found in .env file. LLM calls will fail.")

DEFAULT_LLM_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

RAG_LLM_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

EMBEDDING_MODEL = "mxbai-embed-large"

CHROMA_PERSIST_DIR = Path("rag_db")

DEFAULT_DOCS_DIR = Path("test_docs")