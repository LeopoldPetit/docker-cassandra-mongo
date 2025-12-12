"""
TÂCHE 3 : Agrégation
Calculer le temps de session moyen pour PURCHASE et ADD_TO_CART
"""

import os
import time

# Configuration
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'cassandra')
MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
ES_HOST = os.getenv('ES_HOST', 'elasticsearch')

print("="*60)
print("TÂCHE 3 : Agrégation (session_duration_ms moyen)")
print("="*60)

# ============ MONGODB ============
from pymongo import MongoClient
client = MongoClient(f"mongodb://{MONGO_HOST}:27017/")
collection = client["nosql_tp"]["logs_ecommerce"]

pipeline = [
    {"$match": {"event_type": {"$in": ["PURCHASE", "ADD_TO_CART"]}}},
    {"$group": {
        "_id": "$event_type",
        "avg_duration": {"$avg": "$session_duration_ms"},
        "count": {"$sum": 1}
    }}
]

start = time.time()
results = list(collection.aggregate(pipeline))
mongo_time = (time.time() - start) * 1000

print(f"\nMongoDB          : {mongo_time:.2f} ms")
for r in results:
    print(f"  - {r['_id']}: avg={r['avg_duration']:.2f} ms ({r['count']} events)")
client.close()

# ============ ELASTICSEARCH ============
from elasticsearch import Elasticsearch
es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': 9200, 'scheme': 'http'}])

query = {
    "size": 0,
    "query": {"terms": {"event_type.keyword": ["PURCHASE", "ADD_TO_CART"]}},
    "aggs": {
        "by_event": {
            "terms": {"field": "event_type.keyword"},
            "aggs": {"avg_duration": {"avg": {"field": "session_duration_ms"}}}
        }
    }
}

start = time.time()
try:
    result = es.search(index="ecommerce_logs", body=query)
    es_time = (time.time() - start) * 1000
    print(f"Elasticsearch    : {es_time:.2f} ms")
    for bucket in result['aggregations']['by_event']['buckets']:
        print(f"  - {bucket['key']}: avg={bucket['avg_duration']['value']:.2f} ms ({bucket['doc_count']} events)")
except Exception as e:
    es_time = -1
    print(f"Elasticsearch    : ERREUR (champ non indexé en keyword)")

# ============ CASSANDRA ============
from cassandra.cluster import Cluster
cluster = Cluster([CASSANDRA_HOST], port=9042)
session = cluster.connect("nosql_tp")

start = time.time()
rows_p = list(session.execute("SELECT session_duration_ms FROM logs_by_user WHERE event_type='PURCHASE' ALLOW FILTERING"))
rows_c = list(session.execute("SELECT session_duration_ms FROM logs_by_user WHERE event_type='ADD_TO_CART' ALLOW FILTERING"))
cass_time = (time.time() - start) * 1000

avg_p = sum(r.session_duration_ms for r in rows_p) / len(rows_p) if rows_p else 0
avg_c = sum(r.session_duration_ms for r in rows_c) / len(rows_c) if rows_c else 0

print(f"Cassandra        : {cass_time:.2f} ms (scan complet!)")
print(f"  - PURCHASE: avg={avg_p:.2f} ms ({len(rows_p)} events)")
print(f"  - ADD_TO_CART: avg={avg_c:.2f} ms ({len(rows_c)} events)")
cluster.shutdown()

# ============ RÉSUMÉ ============
print("\n" + "="*60)
print("RÉSUMÉ TÂCHE 3")
print("="*60)
print(f"{'SGBD':<20} {'Temps':>10}")
print("-"*30)
print(f"{'MongoDB':<20} {mongo_time:>8.2f} ms")
if es_time > 0:
    print(f"{'Elasticsearch':<20} {es_time:>8.2f} ms")
else:
    print(f"{'Elasticsearch':<20} {'ERREUR':>10}")
print(f"{'Cassandra':<20} {cass_time:>8.2f} ms")
