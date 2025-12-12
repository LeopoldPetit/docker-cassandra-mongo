# Fichier : elasticsearch_insert.py

import json
import os
from elasticsearch import Elasticsearch, helpers

# Configuration pour Docker
ES_HOST = os.getenv('ES_HOST', 'elasticsearch')
ES_PORT = int(os.getenv('ES_PORT', 9200))
INDEX_NAME = "ecommerce_logs"

def insert_elasticsearch():
    print("Connexion à Elasticsearch...")
    
    es = Elasticsearch(
        hosts=[{'host': ES_HOST, 'port': ES_PORT, 'scheme': 'http'}],
    )
    
    # 1. Vérification de la connexion et suppression de l'index précédent
    try:
        if es.indices.exists(index=INDEX_NAME):
            es.indices.delete(index=INDEX_NAME)
        print(f"Index '{INDEX_NAME}' réinitialisé.")
    except Exception as e:
        print(f"Attention: {e}")

    # 2. Chargement des données
    with open("/app/scripts/data/ecommerce_logs.json", "r") as f:
        data = json.load(f)
        
    print(f"Début de l'indexation de {len(data)} documents...")
    
    # 3. Préparation des actions pour l'insertion en masse (Bulk)
    actions = []
    for log in data:
        action = {
            "_index": INDEX_NAME,
            "_id": log["log_id"], 
            "_source": log
        }
        actions.append(action)

    # 4. Exécution de l'insertion en masse
    try:
        success, errors = helpers.bulk(es, actions)
        
        if not errors:
            print(f"✅ Indexation Elasticsearch terminée. {success} documents indexés.")
        else:
            print(f"❌ Erreur lors de l'indexation. Nombre d'erreurs: {len(errors)}")

    except Exception as e:
        print(f"❌ Erreur critique : {e}")

if __name__ == "__main__":
    insert_elasticsearch()
