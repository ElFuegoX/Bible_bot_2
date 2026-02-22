# Résumé du Contexte de Déploiement : Thomas - Assistant Biblique

Ce document résume l’état actuel, les objectifs et les défis techniques liés au déploiement du projet.

## 🎯 Objectif du Projet
Déployer **Thomas**, un assistant biblique intelligent, sur **Hugging Face Spaces**. L'objectif est de rendre le bot accessible via une interface web (Chainlit) à n'importe quel utilisateur, avec une base de connaissances biblique (RAG).

## 🏗️ Architecture Technique
- **Interface** : [Chainlit](https://chainlit.io/) (Framework Python pour interfaces de chat).
- **Moteur de Recherche (RAG)** : Utilise [LangChain](https://python.langchain.com/) et une base de données vectorielle **FAISS** (`faiss_bible_bdv`).
- **Modèles de Langage (LLM)** : Compatible multi-providers (Google Gemini par défaut, Mistral, Groq).
- **Conteneurisation** : Utilisation de **Docker** pour garantir que l'application tourne de la même manière en local et sur Hugging Face.

## 📍 État Actuel : "Où en est-on ?"
Le projet est techniquement prêt pour le déploiement mais fait face à un blocage spécifique lié aux fichiers de données :

1.  **Configuration terminée** :
    - Le `Dockerfile` est configuré pour Hugging Face (Port 7860, utilisateur sécurisé).
    - Le `README.md` contient les métadonnées nécessaires (SDK Docker, titre, emoji).
    - Les dépendances sont listées dans `requirements.txt`.
2.  **Le Blocage : Git LFS / FAISS** :
    - L'index FAISS (`faiss_bible_bdv`) contient des fichiers binaires.
    - Git "standard" a du mal avec les gros fichiers binaires lors du push vers GitHub ou Hugging Face.
    - **Tentative actuelle** : Nettoyer les configurations Git LFS (`.gitattributes`) pour simplifier l'envoi des données ou trouver une alternative pour charger l'index.

## 🚀 Étapes pour finaliser le déploiement
1.  **Envoi du Code** : Réussir le `git push` complet vers le dépôt distant (Hugging Face ou GitHub lié).
2.  **Configuration des Secrets** : Sur Hugging Face, ajouter les clés API (`GOOGLE_API_KEY`, etc.) dans les "Settings > Variables and Secrets".
3.  **Build Docker** : Hugging Face construira l'image automatiquement à partir du `Dockerfile`.
4.  **Lancement** : Une fois le build fini, l'application sera disponible sur l'URL du Space.

## ⚠️ Points d'Attention
- **Secrets** : Ne jamais pousser le fichier `.env` sur Git. Utiliser impérativement les Secrets de la plateforme.
- **Taille de l'Index** : Si l'index FAISS est trop lourd, il faudra peut-être utiliser Git LFS correctement ou le stocker sur un bucket externe (plus complexe).
