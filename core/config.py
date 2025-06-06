import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not found in .env file. LLM calls will fail.")

DEFAULT_LLM_MODEL = "google/gemma-3-27b-it:free"