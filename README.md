---
title: Thomas - Assistant Biblique 📖
emoji: 📖
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 📖 Thomas - Assistant Biblique

Un chatbot intelligent spécialisé dans la Bible et la théologie, propulsé par l'intelligence artificielle.

## ✨ Fonctionnalités

- 💬 **Chat interactif** — Pose des questions sur la Bible et reçois des réponses contextualisées
- 🤖 **Multi-LLM** — Choisis entre Google Gemini, Mistral AI, ou Groq (Llama 3.3)
- 📚 **Sources bibliques** — Chaque réponse cite les passages pertinents (RAG via FAISS)
- 🧠 **Mémoire** — Thomas se souvient du contexte de la conversation
- 📎 **Upload de textes** — Envoie un fichier (.txt, .md) pour analyse biblique
- 🎯 **Suggestions** — Questions prédéfinies pour démarrer rapidement
- 🌙 **Mode sombre / clair** — Thème premium adaptatif

## 🚀 Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/ElFuegoX/Bible_bot_2.git
cd Bible_bot_2
```

### 2. Créer un environnement virtuel
```bash
python -m venv bible_env
source bible_env/bin/activate  # Linux/Mac
bible_env\Scripts\activate     # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les clés API

Créez un fichier `.env` à la racine du projet :
```env
GOOGLE_API_KEY=votre_clé_gemini
MISTRAL_API_KEY=votre_clé_mistral
GROQ_API_KEY=votre_clé_groq
HF_TOKEN=votre_token_huggingface
```

**Où obtenir les clés :**
| Provider | Lien |
|----------|------|
| Google Gemini | [aistudio.google.com](https://aistudio.google.com/apikey) |
| Mistral AI | [console.mistral.ai](https://console.mistral.ai/api-keys/) |
| Groq | [console.groq.com](https://console.groq.com/keys) |
| HuggingFace | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |

> 💡 Seule la clé du provider par défaut (Gemini) est requise. Les autres sont optionnelles.

### 5. Lancer l'application
```bash
chainlit run app.py -w
```

L'application s'ouvre automatiquement sur `http://localhost:8000`.

## 📁 Structure du projet

```
Bible_bot_2/
├── app.py               # Interface Chainlit (point d'entrée)
├── config.py            # Configuration centralisée
├── llm_providers.py     # Factory multi-LLM
├── rag_engine.py        # Moteur RAG (FAISS + LangChain)
├── prompts.py           # Templates de prompts
├── requirements.txt     # Dépendances Python
├── chainlit.md          # Page d'accueil
├── faiss_bible_bdv/     # Index vectoriel de la Bible
└── public/              # Assets (logos, thème, CSS)
```

## 🛠️ Technologies

- **[Chainlit](https://chainlit.io/)** — Interface conversationnelle
- **[LangChain](https://python.langchain.com/)** — Framework RAG
- **[FAISS](https://faiss.ai/)** — Recherche vectorielle
- **[HuggingFace](https://huggingface.co/)** — Embeddings

---

👨💻 Créé par [El Fuego](https://www.linkedin.com/mélon-joanès-afagnibo-88237a33a)  
*« Cherchez, et vous trouverez. » — Matthieu 7:7*