FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les scripts
COPY scripts/ ./scripts/

# Commande par défaut
CMD ["python", "scripts/main.py"]
