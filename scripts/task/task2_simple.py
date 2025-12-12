"""
TÂCHE 2 : Accès Ciblé et Tri Massif (Haute Disponibilité)
Objectif : Afficher les 100 derniers logs (les plus récents) de l'utilisateur user_id=10

EXPLICATIONS DE PERTINENCE :

CASSANDRA :
- La requête SELECT est basée sur la clé de partition (user_id)
- Le tri est GARANTI par la clé de clustering (timestamp DESC) 
- Cassandra garantit la rapidité même avec des milliards de logs car :
  * Les données sont partitionnées par user_id (accès direct O(1) à la partition)
  * Le tri est pré-calculé au moment de l'écriture (pas de tri à la lecture)
  * Seule la partition de l'utilisateur 10 est lue, pas les autres données

MONGODB :
- Requête find avec filtre sur user_id et tri sur timestamp
- SANS index composé : MongoDB doit scanner tous les documents de l'utilisateur
  puis les trier en mémoire → LENT avec beaucoup de données
- AVEC index composé {user_id: 1, timestamp: -1} : accès direct et tri optimisé
"""

import os
import time

# Configuration
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'cassandra')
MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
ES_HOST = os.getenv('ES_HOST', 'elasticsearch')

print("="*60)
print("TÂCHE 2 : Accès Ciblé (user_id=10, 100 derniers logs)")
print("="*60)

# ============ CASSANDRA ============
from cassandra.cluster import Cluster
cluster = Cluster([CASSANDRA_HOST], port=9042)
session = cluster.connect("nosql_tp")

start = time.time()
rows = list(session.execute("SELECT * FROM logs_by_user WHERE user_id = 10 LIMIT 100"))
cass_time = (time.time() - start) * 1000
cass_count = len(rows)

print(f"\nCassandra        : {cass_count} résultats en {cass_time:.2f} ms")
cluster.shutdown()

# ============ MONGODB ============
from pymongo import MongoClient, DESCENDING
client = MongoClient(f"mongodb://{MONGO_HOST}:27017/")
collection = client["nosql_tp"]["logs_ecommerce"]

# Test SANS index composé (supprimer s'il existe)
collection.drop_index("user_id_1_timestamp_-1") if "user_id_1_timestamp_-1" in [idx['name'] for idx in collection.list_indexes()] else None

start = time.time()
results = list(collection.find({"user_id": 10}).sort("timestamp", -1).limit(100))
mongo_time_no_idx = (time.time() - start) * 1000
mongo_count = len(results)

print(f"MongoDB (sans index): {mongo_count} résultats en {mongo_time_no_idx:.2f} ms")

# Test AVEC index composé
collection.create_index([("user_id", 1), ("timestamp", DESCENDING)], name="idx_user_timestamp")

start = time.time()
results = list(collection.find({"user_id": 10}).sort("timestamp", -1).limit(100))
mongo_time_idx = (time.time() - start) * 1000

print(f"MongoDB (avec index): {mongo_count} résultats en {mongo_time_idx:.2f} ms")
client.close()

# ============ ELASTICSEARCH ============
from elasticsearch import Elasticsearch
es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': 9200, 'scheme': 'http'}])

query = {
    "query": {"term": {"user_id": 10}},
    "sort": [{"timestamp": {"order": "desc"}}],
    "size": 100
}

start = time.time()
result = es.search(index="ecommerce_logs", body=query)
es_time = (time.time() - start) * 1000
es_count = len(result['hits']['hits'])

print(f"Elasticsearch    : {es_count} résultats en {es_time:.2f} ms")

# ============ RÉSUMÉ ============
print("\n" + "="*60)
print("RÉSUMÉ TÂCHE 2")
print("="*60)
print(f"{'SGBD':<25} {'Temps':>10} {'Résultats':>10}")
print("-"*50)
print(f"{'Cassandra':<25} {cass_time:>8.2f} ms {cass_count:>10}")
print(f"{'MongoDB (sans index)':<25} {mongo_time_no_idx:>8.2f} ms {mongo_count:>10}")
print(f"{'MongoDB (avec index)':<25} {mongo_time_idx:>8.2f} ms {mongo_count:>10}")
print(f"{'Elasticsearch':<25} {es_time:>8.2f} ms {es_count:>10}")
