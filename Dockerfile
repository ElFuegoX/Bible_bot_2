FROM python:3.11

# Créer un utilisateur pour des raisons de sécurité
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Installer les dépendances
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers du projet
COPY --chown=user . .

# Exposer le port par défaut de HF Spaces
EXPOSE 7860

# Lancer l'application
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
