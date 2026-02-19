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
from rag_engine import ask


#    Starters (suggestions au lancement)

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Qui est Jésus-Christ ?",
            message="Qui est Jésus-Christ selon la Bible ? Explique son rôle et son importance.",
            icon="/public/logo_light.png",
        ),
        cl.Starter(
            label="Explique Jean 3:16",
            message="Peux-tu m'expliquer le verset Jean 3:16 en détail ?",
            icon="/public/logo_light.png",
        ),
        cl.Starter(
            label="Les 10 Commandements",
            message="Quels sont les 10 commandements et que signifient-ils ?",
            icon="/public/logo_light.png",
        ),
        cl.Starter(
            label="Le pardon dans la Bible",
            message="Que dit la Bible sur le pardon ? Cite les passages importants.",
            icon="/public/logo_light.png",
        ),
    ]


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
            "## 📖 Bienvenue ! Je suis **Thomas**, ton assistant biblique.\n\n"
            "Je peux t'aider avec :\n"
            "- 💬 **Questions** sur la Bible et la théologie\n"
            "- 📜 **Explication** de versets et passages\n"
            "- 📎 **Analyse** de textes que tu m'envoies (upload)\n"
            "- 🔍 **Recherche** de thèmes bibliques\n\n"
            f"Modèle actif : **{LLM_PROVIDERS[DEFAULT_PROVIDER]['label']}**\n\n"
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
    """Gère le changement de LLM ou de température."""
    provider = settings.get("llm_provider", DEFAULT_PROVIDER)
    temperature = settings.get("temperature", DEFAULT_TEMPERATURE)
    
    cl.user_session.set("llm_provider", provider)
    cl.user_session.set("temperature", temperature)
    
    label = LLM_PROVIDERS.get(provider, {}).get("label", provider)
    await cl.Message(
        content=f"✅ Modèle changé : **{label}** | Température : **{temperature}**",
    ).send()


#    Commandes manuelles



    # Récupérer la config de session
    provider = cl.user_session.get("llm_provider", DEFAULT_PROVIDER)
    temperature = cl.user_session.get("temperature", DEFAULT_TEMPERATURE)
    chat_history = cl.user_session.get("chat_history", [])
    
    # Vérifier si un fichier texte a été uploadé
    uploaded_text = ""
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.Text):
                uploaded_text += element.content + "\n"
            elif isinstance(element, cl.File):
                # Lire le contenu du fichier
                try:
                    with open(element.path, "r", encoding="utf-8") as f:
                        uploaded_text += f.read() + "\n"
                except Exception:
                    try:
                        with open(element.path, "r", encoding="latin-1") as f:
                            uploaded_text += f.read() + "\n"
                    except Exception:
                        await cl.Message(
                            content="⚠️ Je n'ai pas pu lire ce fichier. Essayez avec un fichier .txt ou .md."
                        ).send()
                        return
    
    # Construire la question finale
    user_question = message.content
    if uploaded_text:
        from prompts import UPLOAD_ANALYSIS_TEMPLATE
        user_question = UPLOAD_ANALYSIS_TEMPLATE.format(
            uploaded_text=uploaded_text.strip(),
            input=message.content if message.content.strip() else "Analyse ce texte en détail."
        )
    
    # Instancier le LLM
    try:
        llm = get_llm(provider, temperature)
    except ValueError as e:
        await cl.Message(content=f"❌ Erreur de configuration : {e}").send()
        return
    
    # Envoyer un message de chargement
    msg = cl.Message(content="")
    await msg.send()
    
    # Interroger le moteur RAG
    try:
        result = ask(user_question, llm, chat_history)
    except Exception as e:
        msg.content = f"❌ Erreur lors du traitement : {str(e)}"
        await msg.update()
        return
    
    # Afficher la réponse
    msg.content = result["answer"]
    await msg.update()
    
    # Afficher les sources bibliques
    sources = result.get("sources", [])
    if sources:
        source_texts = []
        for i, doc in enumerate(sources, 1):
            # Extraire un extrait du contenu de la source
            content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            source_name = doc.metadata.get("source", f"Source {i}")
            source_texts.append(f"**📄 {source_name}**\n> {content}")
        
        sources_content = "\n\n---\n\n".join(source_texts)
        
        # Envoyer les sources comme éléments
        source_elements = [
            cl.Text(
                name=f"📚 Sources bibliques consultées",
                content=sources_content,
                display="side",
            )
        ]
        
        await cl.Message(
            content="📚 *Sources consultées — cliquez pour voir les passages*",
            elements=source_elements,
        ).send()
    
    # Mettre à jour l'historique
    chat_history.append({"role": "user", "content": message.content})
    chat_history.append({"role": "assistant", "content": result["answer"]})
    
    # Limiter la taille de l'historique
    if len(chat_history) > MAX_HISTORY_MESSAGES * 2:
        chat_history = chat_history[-(MAX_HISTORY_MESSAGES * 2):]
    
    cl.user_session.set("chat_history", chat_history)
