"""
Factory pour instancier les LLMs (Mistral, Gemini, Groq).
"""
import os
from langchain_core.language_models import BaseChatModel
from bot_config import LLM_PROVIDERS, DEFAULT_PROVIDER, DEFAULT_TEMPERATURE



def get_available_providers() -> list[str]:
    """Retourne la liste des providers dont la clé API est configurée."""
    available = []
    for name, info in LLM_PROVIDERS.items():
        if os.getenv(info["env_key"], ""):
            available.append(name)
    return available


def get_llm(provider: str = DEFAULT_PROVIDER, temperature: float = DEFAULT_TEMPERATURE) -> BaseChatModel:
    """
    Instancie le LLM correspondant au provider choisi.
    
    Args:
        provider: Nom du provider ("Gemini", "Mistral", "Groq")
        temperature: Température du modèle (0.0 à 1.0)
    
    Returns:
        Instance BaseChatModel prête à l'emploi
    
    Raises:
        ValueError: Si le provider est inconnu ou la clé API manquante
    """
    if provider not in LLM_PROVIDERS:
        raise ValueError(f"Provider inconnu : {provider}. Choix possibles : {list(LLM_PROVIDERS.keys())}")
    
    info = LLM_PROVIDERS[provider]
    api_key = os.getenv(info["env_key"], "")
    
    if not api_key:
        raise ValueError(
            f"Clé API manquante pour {provider}. "
            f"Ajoutez {info['env_key']} dans votre fichier .env"
        )
    
    if provider == "Gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=info["model"],
            temperature=temperature,
            google_api_key=api_key,
        )
    
    elif provider == "Mistral":
        from langchain_mistralai import ChatMistralAI
        return ChatMistralAI(
            model=info["model"],
            temperature=temperature,
            mistral_api_key=api_key,
        )
    
    elif provider == "Groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=info["model"],
            temperature=temperature,
            groq_api_key=api_key,
        )
    
    raise ValueError(f"Provider non implémenté : {provider}")
