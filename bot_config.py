"""
Configuration centralisée pour Bible Bot Thomas.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Clés API
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# Embeddings
EMBEDDING_MODEL = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"

# FAISS
FAISS_INDEX_PATH = "faiss_bible_bdv"

# Retriever
SEARCH_TYPE = "similarity"
SEARCH_K = 4  # Nombre de documents récupérés

# LLM Providers
LLM_PROVIDERS = {
    "Gemini": {
        "model": "gemini-2.0-flash",
        "env_key": "GOOGLE_API_KEY",
        "label": "Google Gemini ",
    },
    "Mistral": {
        "model": "mistral-large-latest",
        "env_key": "MISTRAL_API_KEY",
        "label": "Mistral AI ",
    },
    "Groq": {
        "model": "llama-3.3-70b-versatile",
        "env_key": "GROQ_API_KEY",
        "label": "Groq (Llama 3.3) ",
    },
}

DEFAULT_PROVIDER = "Gemini"
DEFAULT_TEMPERATURE = 0.3

# Conversation
MAX_HISTORY_MESSAGES = 10  # Paires de messages gardées en mémoire
