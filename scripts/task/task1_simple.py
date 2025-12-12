"""
TÂCHE 1 : Recherche Full-Text
Trouver les événements ERROR_404 d'octobre 2025 avec "critique" dans la description
"""

import os
import time

# Configuration
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'cassandra')
MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
ES_HOST = os.getenv('ES_HOST', 'elasticsearch')

print("="*60)
print("TÂCHE 1 : Recherche Full-Text")
print("="*60)

# ============ ELASTICSEARCH ============
from elasticsearch import Elasticsearch
es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': 9200, 'scheme': 'http'}])

query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"description": "critique failed"}},
                {"range": {"timestamp": {"gte": "2025-10-01", "lte": "2025-10-31"}}}
            ],
            "filter": [{"term": {"event_type.keyword": "ERROR_404"}}]
        }
    }
}

start = time.time()
result = es.search(index="ecommerce_logs", body=query, size=1000)
es_time = (time.time() - start) * 1000
es_count = result['hits']['total']['value']

print(f"\nElasticsearch : {es_count} résultats en {es_time:.2f} ms")

# ============ MONGODB ============
from pymongo import MongoClient
client = MongoClient(f"mongodb://{MONGO_HOST}:27017/")
collection = client["nosql_tp"]["logs_ecommerce"]

# Avec $regex
start = time.time()
results = list(collection.find({
    "event_type": "ERROR_404",
    "timestamp": {"$gte": "2025-10-01", "$lte": "2025-10-31"},
    "description": {"$regex": "critique|failed", "$options": "i"}
}))
mongo_time = (time.time() - start) * 1000
mongo_count = len(results)

print(f"MongoDB ($regex) : {mongo_count} résultats en {mongo_time:.2f} ms")

# Avec index $text
start = time.time()
try:
    results = list(collection.find({
        "$text": {"$search": "critique failed"},
        "event_type": "ERROR_404"
    }))
    mongo_text_time = (time.time() - start) * 1000
    mongo_text_count = len(results)
    print(f"MongoDB ($text)  : {mongo_text_count} résultats en {mongo_text_time:.2f} ms")
except:
    print("MongoDB ($text)  : Index non disponible")

client.close()

# ============ CASSANDRA ============
from cassandra.cluster import Cluster
cluster = Cluster([CASSANDRA_HOST], port=9042)
session = cluster.connect("nosql_tp")

start = time.time()
rows = list(session.execute("SELECT * FROM logs_by_user WHERE event_type = 'ERROR_404' ALLOW FILTERING"))
filtered = [r for r in rows if 'critique' in r.description.lower()]
cass_time = (time.time() - start) * 1000
cass_count = len(filtered)

print(f"Cassandra        : {cass_count} résultats en {cass_time:.2f} ms (scan complet!)")

cluster.shutdown()

# ============ RÉSUMÉ ============
print("\n" + "="*60)
print("RÉSUMÉ TÂCHE 1")
print("="*60)
print(f"{'SGBD':<20} {'Temps':>10} {'Résultats':>10}")
print("-"*40)
print(f"{'Elasticsearch':<20} {es_time:>8.2f} ms {es_count:>10}")
print(f"{'MongoDB':<20} {mongo_time:>8.2f} ms {mongo_count:>10}")
print(f"{'Cassandra':<20} {cass_time:>8.2f} ms {cass_count:>10}")
