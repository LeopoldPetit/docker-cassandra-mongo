# Fichier : mongo_insert.py

import json
import os
from pymongo import MongoClient

# Configuration pour Docker
MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
DB_NAME = "nosql_tp"
COLLECTION_NAME = "logs_ecommerce"

def insert_mongo():
    print("Connexion à MongoDB...")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Effacer l'ancienne collection pour un test propre
    collection.drop()

    print(f"Chargement de 'ecommerce_logs.json'...")
    with open("/app/scripts/data/ecommerce_logs.json", "r") as f:
        data = json.load(f)

    print(f"Début de l'insertion de {len(data)} documents...")
    
    # Insertion en masse pour de meilleures performances
    collection.insert_many(data)

    print(f"✅ Insertion MongoDB terminée. {len(data)} documents insérés.")
    
    # Création d'index pour accélérer les requêtes
    collection.create_index("user_id")
    print("Index 'user_id' créé.")
    
    # Création d'un index texte pour la recherche full-text (Tâche 1)
    collection.create_index([("description", "text")])
    print("Index 'text' sur 'description' créé.")

    client.close()

if __name__ == "__main__":
    insert_mongo()
