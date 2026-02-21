"""
Moteur RAG : chargement FAISS, construction de la chaîne, interrogation.
"""
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage

from bot_config import EMBEDDING_MODEL, FAISS_INDEX_PATH, SEARCH_TYPE, SEARCH_K
from prompts import BIBLE_PROMPT

# ─── Chargement unique des embeddings et de l'index ─────────
_embeddings = None
_db = None
_retriever = None


def _init():
    """Initialise les embeddings et l'index FAISS (chargement paresseux)."""
    global _embeddings, _db, _retriever
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        _db = FAISS.load_local(
            FAISS_INDEX_PATH, _embeddings, allow_dangerous_deserialization=True
        )
        _retriever = _db.as_retriever(
            search_type=SEARCH_TYPE,
            search_kwargs={"k": SEARCH_K},
        )


def get_retriever():
    """Retourne le retriever FAISS (initialise si nécessaire)."""
    _init()
    return _retriever


def create_chain(llm: BaseChatModel):
    """
    Crée une chaîne RAG (retrieval + LLM).
    
    Args:
        llm: Instance du LLM à utiliser
    
    Returns:
        Chaîne de retrieval prête à être invoquée
    """
    _init()
    combine_docs_chain = create_stuff_documents_chain(llm, BIBLE_PROMPT)
    return create_retrieval_chain(_retriever, combine_docs_chain)


def format_history(history: list[dict]) -> list:
    """
    Convertit l'historique de session Chainlit en messages LangChain.
    
    Args:
        history: Liste de dicts {"role": "user"|"assistant", "content": str}
    
    Returns:
        Liste de HumanMessage / AIMessage
    """
    messages = []
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    return messages


def ask(question: str, llm: BaseChatModel, chat_history: list[dict] = None) -> dict:
    """
    Pose une question au moteur RAG.
    
    Args:
        question: La question de l'utilisateur
        llm: Instance du LLM à utiliser
        chat_history: Historique de conversation (optionnel)
    
    Returns:
        Dict avec "answer" (str) et "sources" (list de documents)
    """
    chain = create_chain(llm)
    history_messages = format_history(chat_history or [])
    
    response = chain.invoke({
        "input": question,
        "chat_history": history_messages,
    })
    
    return {
        "answer": response.get("answer", "Je n'ai pas pu formuler une réponse. Reformulez votre question."),
        "sources": response.get("context", []),
    }


async def ask_stream(question: str, llm: BaseChatModel, chat_history: list[dict] = None):
    """
    Générateur asynchrone pour le streaming RAG.
    
    Yields:
        Des chunks de texte (str) pour la réponse.
    """
    chain = create_chain(llm)
    history_messages = format_history(chat_history or [])
    
    async for chunk in chain.astream({
        "input": question,
        "chat_history": history_messages,
    }):
        # Le chunk peut contenir 'context' ou 'answer'
        # On ne veut streamer que l'answer
        if "answer" in chunk:
            yield chunk["answer"]
