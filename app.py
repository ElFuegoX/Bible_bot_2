"""
Thomas - Assistant Biblique 📖
Interface Chainlit avec support multi-LLM, mémoire, sources et upload.
"""
import chainlit as cl
from chainlit.input_widget import Select, Slider

from bot_config import (
    LLM_PROVIDERS, DEFAULT_PROVIDER, DEFAULT_TEMPERATURE,
    MAX_HISTORY_MESSAGES,
)
from llm_providers import get_llm, get_available_providers
from rag_engine import ask, ask_stream


# Chat Settings (panneau de réglages)

def build_settings():
    """Construit les widgets du panneau Settings."""
    available = get_available_providers()
    # S'assurer que le provider par défaut est dans la liste
    default = DEFAULT_PROVIDER if DEFAULT_PROVIDER in available else (available[0] if available else "Gemini")
    
    provider_labels = {name: LLM_PROVIDERS[name]["label"] for name in available}
    
    return [
        Select(
            id="llm_provider",
            label="🤖 Modèle LLM",
            description="Choisissez le modèle d'intelligence artificielle",
            values=available,
            initial_value=default,
        ),
        Slider(
            id="temperature",
            label="🌡️ Température",
            description="Plus bas = plus précis, plus haut = plus créatif",
            min=0.0,
            max=1.0,
            step=0.1,
            initial=DEFAULT_TEMPERATURE,
        ),
    ]


# Démarrage de la conversation

@cl.on_chat_start
async def on_chat_start():
    """Initialisation de chaque nouvelle session."""
    # Initialiser l'historique
    cl.user_session.set("chat_history", [])
    cl.user_session.set("llm_provider", DEFAULT_PROVIDER)
    cl.user_session.set("temperature", DEFAULT_TEMPERATURE)
    
    # Message de bienvenue
    await cl.Message(
        content=(
            "## 📖 Bienvenue ! Je suis Thomas, ton assistant biblique.\n\n"
            "Je peux t'aider avec :\n"
            "- 💬 **Questions** sur la Bible et la théologie\n"
            "- 📜 **Explication** de versets et passages\n"
            "-  **Recherche** de thèmes bibliques\n\n"
            f"Modèle actif : {LLM_PROVIDERS[DEFAULT_PROVIDER]['label']}\n\n"
            "---\n"
            "*Pose ta question ci-dessous ou clique sur une suggestion !*"
        ),
    ).send()

    # Afficher les réglages directement dans le chat (plus visible)
    settings = build_settings()
    await cl.ChatSettings(settings).send()


# Mise à jour des Settings

@cl.on_settings_update
async def on_settings_update(settings):
    """Gère le changement de provider et de température."""    
    provider = settings.get("llm_provider", DEFAULT_PROVIDER)
    temperature = settings.get("temperature", DEFAULT_TEMPERATURE)
    
    cl.user_session.set("llm_provider", provider)
    cl.user_session.set("temperature", temperature)
    
    label = LLM_PROVIDERS.get(provider, {}).get("label", provider)
    
    await cl.Message(
        content=f"✅ Paramètres mis à jour :\n- Modèle : {label}\n- Température : {temperature}",
    ).send()


@cl.on_message
async def main(message: cl.Message):
    # Récupérer la config de session
    provider = cl.user_session.get("llm_provider", DEFAULT_PROVIDER)
    temperature = cl.user_session.get("temperature", DEFAULT_TEMPERATURE)
    chat_history = cl.user_session.get("chat_history", [])
    
    # Construire la question finale
    user_question = message.content
    
    # Instancier le LLM
    try:
        llm = get_llm(provider, temperature)
    except ValueError as e:
        await cl.Message(content=f"❌ Erreur de configuration : {e}").send()
        return
    
    # Envoyer un message vide qui servira de base pour le stream
    msg = cl.Message(content="")
    
    # Interroger le moteur RAG en mode streaming
    full_answer = ""
    try:
        async for chunk in ask_stream(user_question, llm, chat_history):
            if chunk:
                full_answer += chunk
                await msg.stream_token(chunk)
    except Exception as e:
        if not full_answer:
            msg.content = f"❌ Erreur lors du traitement : {str(e)}"
            await msg.send()
        else:
            await cl.Message(content=f"\n\n⚠️ Erreur partielle : {str(e)}").send()
        return
    
    await msg.send()
    
    # Mettre à jour l'historique
    chat_history.append({"role": "user", "content": message.content})
    chat_history.append({"role": "assistant", "content": full_answer})
    
    # Limiter la taille de l'historique
    if len(chat_history) > MAX_HISTORY_MESSAGES * 2:
        chat_history = chat_history[-(MAX_HISTORY_MESSAGES * 2):]
    
    cl.user_session.set("chat_history", chat_history)
