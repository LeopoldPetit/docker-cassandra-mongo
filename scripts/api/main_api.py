"""
API REST unifiée pour le TP NoSQL
Expose Cassandra, MongoDB et Elasticsearch via une API REST unique
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from cassandra.cluster import Cluster
from pymongo import MongoClient, DESCENDING
from elasticsearch import Elasticsearch
import os
import time

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin depuis React

# Configuration
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'cassandra')
CASSANDRA_PORT = int(os.getenv('CASSANDRA_PORT', 9042))
MONGO_HOST = os.getenv('MONGO_HOST', 'mongo')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
ES_HOST = os.getenv('ES_HOST', 'elasticsearch')
ES_PORT = int(os.getenv('ES_PORT', 9200))


# ============================================================================
# CONNEXIONS
# ============================================================================

def get_cassandra_session():
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
    session = cluster.connect("nosql_tp")
    return cluster, session

def get_mongo_collection():
    client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/")
    return client, client["nosql_tp"]["logs_ecommerce"]

def get_elasticsearch():
    return Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT, 'scheme': 'http'}])


# ============================================================================
# ENDPOINTS SANTÉ
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Vérification de santé de l'API"""
    status = {"api": "ok", "databases": {}}
    
    # Test Cassandra
    try:
        cluster, session = get_cassandra_session()
        session.execute("SELECT now() FROM system.local")
        status["databases"]["cassandra"] = "ok"
        cluster.shutdown()
    except Exception as e:
        status["databases"]["cassandra"] = f"error: {str(e)}"
    
    # Test MongoDB
    try:
        client, _ = get_mongo_collection()
        client.admin.command('ping')
        status["databases"]["mongodb"] = "ok"
        client.close()
    except Exception as e:
        status["databases"]["mongodb"] = f"error: {str(e)}"
    
    # Test Elasticsearch
    try:
        es = get_elasticsearch()
        es.cluster.health()
        status["databases"]["elasticsearch"] = "ok"
    except Exception as e:
        status["databases"]["elasticsearch"] = f"error: {str(e)}"
    
    return jsonify(status)


# ============================================================================
# TÂCHE 1 : Recherche Full-Text
# ============================================================================

@app.route('/api/task1', methods=['POST'])
def task1_fulltext_search():
    """
    Tâche 1 : Recherche Full-Text
    Trouver les événements ERROR_404 d'octobre 2025 avec "critique" dans la description
    """
    data = request.json or {}
    event_type = data.get('event_type', 'ERROR_404')
    search_text = data.get('search_text', 'critique')
    date_start = data.get('date_start', '2025-10-01')
    date_end = data.get('date_end', '2025-10-31')
    
    results = {
        "task": "Tâche 1 - Recherche Full-Text",
        "params": {
            "event_type": event_type,
            "search_text": search_text,
            "date_range": f"{date_start} - {date_end}"
        },
        "databases": {}
    }
    
    # ============ ELASTICSEARCH ============
    try:
        es = get_elasticsearch()
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"description": search_text}},
                        {"range": {"timestamp": {"gte": date_start, "lte": date_end}}}
                    ],
                    "filter": [{"term": {"event_type.keyword": event_type}}]
                }
            },
            "track_total_hits": True
        }
        start = time.time()
        result = es.search(index="ecommerce_logs", body=query, size=100)
        exec_time = (time.time() - start) * 1000
        
        results["databases"]["elasticsearch"] = {
            "count": result['hits']['total']['value'],
            "execution_time_ms": round(exec_time, 2),
            "status": "success",
            "sample_data": [hit['_source'] for hit in result['hits']['hits'][:5]]
        }
    except Exception as e:
        results["databases"]["elasticsearch"] = {"status": "error", "error": str(e)}
    
    # ============ MONGODB ============
    try:
        client, collection = get_mongo_collection()
        start = time.time()
        mongo_results = list(collection.find({
            "event_type": event_type,
            "timestamp": {"$gte": date_start, "$lte": date_end},
            "description": {"$regex": search_text, "$options": "i"}
        }))
        exec_time = (time.time() - start) * 1000
        
        # Convertir ObjectId en string
        for doc in mongo_results:
            doc['_id'] = str(doc['_id'])
        
        results["databases"]["mongodb"] = {
            "count": len(mongo_results),
            "execution_time_ms": round(exec_time, 2),
            "status": "success",
            "sample_data": mongo_results[:5]
        }
        client.close()
    except Exception as e:
        results["databases"]["mongodb"] = {"status": "error", "error": str(e)}
    
    # ============ CASSANDRA ============
    try:
        cluster, session = get_cassandra_session()
        start = time.time()
        # Scan complet car Cassandra n'est pas optimisé pour ce type de requête
        rows = list(session.execute("SELECT * FROM logs_by_user"))
        # Filtrage côté Python (dates + event_type + texte)
        from datetime import datetime
        date_start_dt = datetime.fromisoformat(date_start)
        date_end_dt = datetime.fromisoformat(date_end + "T23:59:59")
        
        filtered = [
            r for r in rows 
            if r.event_type == event_type 
            and date_start_dt <= r.timestamp <= date_end_dt
            and search_text.lower() in r.description.lower()
        ]
        exec_time = (time.time() - start) * 1000
        
        results["databases"]["cassandra"] = {
            "count": len(filtered),
            "execution_time_ms": round(exec_time, 2),
            "status": "success",
            "note": "Scan complet + filtrage côté client",
            "sample_data": [dict(r._asdict()) for r in filtered[:5]]
        }
        cluster.shutdown()
    except Exception as e:
        results["databases"]["cassandra"] = {"status": "error", "error": str(e)}
    
    return jsonify(results)


# ============================================================================
# TÂCHE 2 : Accès Ciblé et Tri
# ============================================================================

@app.route('/api/task2', methods=['POST'])
def task2_user_logs():
    """
    Tâche 2 : Accès Ciblé et Tri
    Récupérer les 100 derniers logs d'un utilisateur
    """
    data = request.json or {}
    user_id = data.get('user_id', 10)
    limit = data.get('limit', 100)
    
    results = {
        "task": "Tâche 2 - Accès Ciblé et Tri",
        "params": {"user_id": user_id, "limit": limit},
        "databases": {}
    }
    
    # ============ CASSANDRA ============
    try:
        cluster, session = get_cassandra_session()
        start = time.time()
        rows = list(session.execute(
            f"SELECT * FROM logs_by_user WHERE user_id = {user_id} LIMIT {limit}"
        ))
        exec_time = (time.time() - start) * 1000
        
        results["databases"]["cassandra"] = {
            "count": len(rows),
            "execution_time_ms": round(exec_time, 2),
            "status": "success",
            "note": "Optimisé: clé de partition + clustering",
            "sample_data": [dict(r._asdict()) for r in rows[:5]]
        }
        cluster.shutdown()
    except Exception as e:
        results["databases"]["cassandra"] = {"status": "error", "error": str(e)}
    
    # ============ MONGODB ============
    try:
        client, collection = get_mongo_collection()
        start = time.time()
        mongo_results = list(
            collection.find({"user_id": user_id})
            .sort("timestamp", DESCENDING)
            .limit(limit)
        )
        exec_time = (time.time() - start) * 1000
        
        for doc in mongo_results:
            doc['_id'] = str(doc['_id'])
        
        results["databases"]["mongodb"] = {
            "count": len(mongo_results),
            "execution_time_ms": round(exec_time, 2),
            "status": "success",
            "note": "Avec index composé recommandé",
            "sample_data": mongo_results[:5]
        }
        client.close()
    except Exception as e:
        results["databases"]["mongodb"] = {"status": "error", "error": str(e)}
    
    # ============ ELASTICSEARCH ============
    try:
        es = get_elasticsearch()
        query = {
            "query": {"term": {"user_id": user_id}},
            "sort": [{"timestamp": {"order": "desc"}}],
            "size": limit
        }
        start = time.time()
        result = es.search(index="ecommerce_logs", body=query)
        exec_time = (time.time() - start) * 1000
        
        results["databases"]["elasticsearch"] = {
            "count": len(result['hits']['hits']),
            "execution_time_ms": round(exec_time, 2),
            "status": "success",
            "sample_data": [hit['_source'] for hit in result['hits']['hits'][:5]]
        }
    except Exception as e:
        results["databases"]["elasticsearch"] = {"status": "error", "error": str(e)}
    
    return jsonify(results)


# ============================================================================
# TÂCHE 3 : Agrégation
# ============================================================================

@app.route('/api/task3', methods=['POST'])
def task3_aggregation():
    """
    Tâche 3 : Agrégation
    Calculer le temps de session moyen par type d'événement
    """
    data = request.json or {}
    event_types = data.get('event_types', ['PURCHASE', 'ADD_TO_CART'])
    
    results = {
        "task": "Tâche 3 - Agrégation",
        "params": {"event_types": event_types},
        "databases": {}
    }
    
    # ============ MONGODB ============
    try:
        client, collection = get_mongo_collection()
        pipeline = [
            {"$match": {"event_type": {"$in": event_types}}},
            {"$group": {
                "_id": "$event_type",
                "avg_duration": {"$avg": "$session_duration_ms"},
                "count": {"$sum": 1},
                "min_duration": {"$min": "$session_duration_ms"},
                "max_duration": {"$max": "$session_duration_ms"}
            }}
        ]
        start = time.time()
        mongo_results = list(collection.aggregate(pipeline))
        exec_time = (time.time() - start) * 1000
        
        aggregations = {}
        for r in mongo_results:
            aggregations[r['_id']] = {
                "count": r['count'],
                "avg_duration": round(r['avg_duration'], 2),
                "min_duration": r['min_duration'],
                "max_duration": r['max_duration']
            }
        
        results["databases"]["mongodb"] = {
            "execution_time_ms": round(exec_time, 2),
            "status": "success",
            "aggregations": aggregations
        }
        client.close()
    except Exception as e:
        results["databases"]["mongodb"] = {"status": "error", "error": str(e)}
    
    # ============ ELASTICSEARCH ============
    try:
        es = get_elasticsearch()
        query = {
            "size": 0,
            "query": {"terms": {"event_type.keyword": event_types}},
            "aggs": {
                "by_event_type": {
                    "terms": {"field": "event_type.keyword"},
                    "aggs": {
                        "avg_duration": {"avg": {"field": "session_duration_ms"}},
                        "min_duration": {"min": {"field": "session_duration_ms"}},
                        "max_duration": {"max": {"field": "session_duration_ms"}}
                    }
                }
            }
        }
        start = time.time()
        result = es.search(index="ecommerce_logs", body=query)
        exec_time = (time.time() - start) * 1000
        
        aggregations = {}
        for bucket in result['aggregations']['by_event_type']['buckets']:
            aggregations[bucket['key']] = {
                "count": bucket['doc_count'],
                "avg_duration": round(bucket['avg_duration']['value'], 2),
                "min_duration": bucket['min_duration']['value'],
                "max_duration": bucket['max_duration']['value']
            }
        
        results["databases"]["elasticsearch"] = {
            "execution_time_ms": round(exec_time, 2),
            "status": "success",
            "aggregations": aggregations
        }
    except Exception as e:
        results["databases"]["elasticsearch"] = {"status": "error", "error": str(e)}
    
    # ============ CASSANDRA ============
    try:
        cluster, session = get_cassandra_session()
        start = time.time()
        aggregations = {}
        
        for event_type in event_types:
            rows = list(session.execute(
                f"SELECT session_duration_ms FROM logs_by_user WHERE event_type = '{event_type}' ALLOW FILTERING"
            ))
            if rows:
                durations = [r.session_duration_ms for r in rows if r.session_duration_ms]
                aggregations[event_type] = {
                    "count": len(rows),
                    "avg_duration": round(sum(durations) / len(durations), 2) if durations else 0,
                    "min_duration": min(durations) if durations else 0,
                    "max_duration": max(durations) if durations else 0
                }
        
        exec_time = (time.time() - start) * 1000
        
        results["databases"]["cassandra"] = {
            "execution_time_ms": round(exec_time, 2),
            "status": "success",
            "note": "Scan complet + agrégation côté client",
            "aggregations": aggregations
        }
        cluster.shutdown()
    except Exception as e:
        results["databases"]["cassandra"] = {"status": "error", "error": str(e)}
    
    return jsonify(results)


# ============================================================================
# EXÉCUTER TOUTES LES TÂCHES
# ============================================================================

@app.route('/api/all-tasks', methods=['POST'])
def all_tasks():
    """Exécute les 3 tâches et retourne tous les résultats"""
    return jsonify({
        "task1": task1_fulltext_search().get_json(),
        "task2": task2_user_logs().get_json(),
        "task3": task3_aggregation().get_json()
    })


# ============================================================================
# GESTION DES DONNÉES
# ============================================================================

@app.route('/api/data/stats', methods=['GET'])
def get_data_stats():
    """Retourne le nombre de documents dans chaque base"""
    stats = {}
    
    # Cassandra
    try:
        cluster, session = get_cassandra_session()
        rows = list(session.execute("SELECT COUNT(*) as count FROM logs_by_user"))
        stats["cassandra"] = rows[0].count if rows else 0
        cluster.shutdown()
    except Exception as e:
        stats["cassandra"] = f"error: {str(e)}"
    
    # MongoDB
    try:
        client, collection = get_mongo_collection()
        stats["mongodb"] = collection.count_documents({})
        client.close()
    except Exception as e:
        stats["mongodb"] = f"error: {str(e)}"
    
    # Elasticsearch
    try:
        es = get_elasticsearch()
        if es.indices.exists(index="ecommerce_logs"):
            result = es.count(index="ecommerce_logs")
            stats["elasticsearch"] = result['count']
        else:
            stats["elasticsearch"] = 0
    except Exception as e:
        stats["elasticsearch"] = f"error: {str(e)}"
    
    return jsonify(stats)


@app.route('/api/data/clear', methods=['POST'])
def clear_all_data():
    """Vide toutes les bases de données"""
    results = {}
    
    # Cassandra
    try:
        cluster, session = get_cassandra_session()
        session.execute("TRUNCATE logs_by_user")
        results["cassandra"] = "cleared"
        cluster.shutdown()
    except Exception as e:
        results["cassandra"] = f"error: {str(e)}"
    
    # MongoDB
    try:
        client, collection = get_mongo_collection()
        collection.delete_many({})
        results["mongodb"] = "cleared"
        client.close()
    except Exception as e:
        results["mongodb"] = f"error: {str(e)}"
    
    # Elasticsearch
    try:
        es = get_elasticsearch()
        if es.indices.exists(index="ecommerce_logs"):
            es.indices.delete(index="ecommerce_logs")
        results["elasticsearch"] = "cleared"
    except Exception as e:
        results["elasticsearch"] = f"error: {str(e)}"
    
    return jsonify({"status": "success", "results": results})


@app.route('/api/data/generate', methods=['POST'])
def generate_and_insert_data():
    """Génère et insère des données dans toutes les bases"""
    import uuid
    import random
    from datetime import datetime, timedelta
    from cassandra.query import BatchStatement
    from elasticsearch import helpers
    
    data = request.json or {}
    num_logs = data.get('num_logs', 10000)
    num_users = data.get('num_users', 1000)
    num_products = data.get('num_products', 100)
    
    # Limiter pour éviter les abus
    num_logs = min(num_logs, 500000)
    
    results = {
        "requested": num_logs,
        "databases": {}
    }
    
    # ============ GÉNÉRATION DES DONNÉES ============
    logs = []
    events = ["VIEW_PRODUCT", "ADD_TO_CART", "PURCHASE", "ERROR_404", "LOGOUT", "SEARCH"]
    products = [f"PROD_{i:03d}" for i in range(1, num_products + 1)]
    users = list(range(1, num_users + 1))
    start_time = datetime(2025, 10, 1, 0, 0, 0)
    
    for _ in range(num_logs):
        event_type = random.choice(events)
        log_time = start_time + timedelta(seconds=random.randint(1, 3600*24*30))
        
        log = {
            "log_id": str(uuid.uuid4()),
            "timestamp": log_time.isoformat(),
            "user_id": random.choice(users),
            "event_type": event_type,
            "product_id": random.choice(products) if "PRODUCT" in event_type or "CART" in event_type else None,
            "session_duration_ms": random.randint(100, 60000),
            "description": f"Event {event_type} processed.",
        }
        
        if event_type == "ERROR_404":
            log["description"] = "Page introuvable. Erreur critique."
        elif event_type == "PURCHASE":
            log["description"] = f"Transaction finale réussie pour produit {log['product_id']}."
            
        logs.append(log)
    
    # ============ INSERTION CASSANDRA ============
    try:
        cluster, session = get_cassandra_session()
        
        prepared_stmt = session.prepare(
            "INSERT INTO logs_by_user (user_id, timestamp, log_id, event_type, product_id, description, session_duration_ms) VALUES (?, ?, ?, ?, ?, ?, ?)"
        )
        
        batch = BatchStatement()
        batch_size = 100
        inserted = 0
        
        for i, log in enumerate(logs):
            ts = datetime.fromisoformat(log["timestamp"])
            batch.add(prepared_stmt, (
                log["user_id"],
                ts,
                uuid.UUID(log["log_id"]),
                log["event_type"],
                log.get("product_id"),
                log["description"],
                log["session_duration_ms"]
            ))
            
            if (i + 1) % batch_size == 0:
                session.execute(batch)
                batch = BatchStatement()
                inserted += batch_size
        
        # Insérer le reste
        if len(logs) % batch_size != 0:
            session.execute(batch)
            inserted += len(logs) % batch_size
        
        results["databases"]["cassandra"] = {"status": "success", "inserted": inserted}
        cluster.shutdown()
    except Exception as e:
        results["databases"]["cassandra"] = {"status": "error", "error": str(e)}
    
    # ============ INSERTION ELASTICSEARCH ============
    # Faire AVANT MongoDB car insert_many modifie les objets en ajoutant _id
    try:
        es = get_elasticsearch()
        
        # Créer l'index s'il n'existe pas
        if not es.indices.exists(index="ecommerce_logs"):
            es.indices.create(index="ecommerce_logs")
        
        actions = [
            {"_index": "ecommerce_logs", "_id": log["log_id"], "_source": log}
            for log in logs
        ]
        
        success, _ = helpers.bulk(es, actions)
        results["databases"]["elasticsearch"] = {"status": "success", "inserted": success}
    except Exception as e:
        results["databases"]["elasticsearch"] = {"status": "error", "error": str(e)}
    
    # ============ INSERTION MONGODB ============
    # Faire APRÈS Elasticsearch car insert_many ajoute _id aux objets
    try:
        client, collection = get_mongo_collection()
        collection.insert_many(logs)
        results["databases"]["mongodb"] = {"status": "success", "inserted": len(logs)}
        client.close()
    except Exception as e:
        results["databases"]["mongodb"] = {"status": "error", "error": str(e)}
    
    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
