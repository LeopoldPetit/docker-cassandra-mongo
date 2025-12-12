"""
API REST pour exposer Cassandra à n8n
"""

from flask import Flask, request, jsonify
from cassandra.cluster import Cluster
import os
import time

app = Flask(__name__)

CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'cassandra')
CASSANDRA_PORT = int(os.getenv('CASSANDRA_PORT', 9042))

def get_session():
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
    session = cluster.connect("nosql_tp")
    return cluster, session


@app.route('/health', methods=['GET'])
def health():
    """Vérification de santé de l'API"""
    return jsonify({"status": "ok"})


@app.route('/query', methods=['POST'])
def execute_query():
    """
    Exécute une requête CQL
    Body: {"query": "SELECT * FROM table", "params": []}
    """
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    cluster, session = get_session()
    try:
        start = time.time()
        rows = list(session.execute(query))
        exec_time = (time.time() - start) * 1000
        
        # Convertir les rows en dictionnaires
        results = []
        for row in rows:
            results.append(dict(row._asdict()))
        
        return jsonify({
            "success": True,
            "count": len(results),
            "execution_time_ms": round(exec_time, 2),
            "data": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cluster.shutdown()


@app.route('/logs/search', methods=['POST'])
def search_logs():
    """
    Recherche dans les logs avec filtres
    Body: {
        "event_type": "ERROR_404",
        "description_contains": "critique",
        "date_start": "2025-10-01",
        "date_end": "2025-10-31"
    }
    """
    data = request.json
    event_type = data.get('event_type')
    description_filter = data.get('description_contains', '').lower()
    date_start = data.get('date_start')
    date_end = data.get('date_end')
    
    cluster, session = get_session()
    try:
        start = time.time()
        
        # Requête de base
        query = "SELECT * FROM logs_by_user"
        conditions = []
        
        if event_type:
            conditions.append(f"event_type = '{event_type}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions) + " ALLOW FILTERING"
        
        rows = list(session.execute(query))
        
        # Filtrage côté Python (Cassandra ne supporte pas LIKE/full-text)
        filtered = []
        for row in rows:
            row_dict = dict(row._asdict())
            
            # Filtre sur description
            if description_filter:
                desc = row_dict.get('description', '').lower()
                if description_filter not in desc:
                    continue
            
            # Filtre sur date
            if date_start and date_end:
                timestamp = str(row_dict.get('timestamp', ''))
                if not (date_start <= timestamp <= date_end):
                    continue
            
            filtered.append(row_dict)
        
        exec_time = (time.time() - start) * 1000
        
        return jsonify({
            "success": True,
            "count": len(filtered),
            "execution_time_ms": round(exec_time, 2),
            "data": filtered
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cluster.shutdown()


@app.route('/logs/by-user/<user_id>', methods=['GET'])
def get_logs_by_user(user_id):
    """Récupère les logs d'un utilisateur spécifique"""
    cluster, session = get_session()
    try:
        start = time.time()
        rows = list(session.execute(
            "SELECT * FROM logs_by_user WHERE user_id = %s",
            [user_id]
        ))
        exec_time = (time.time() - start) * 1000
        
        results = [dict(row._asdict()) for row in rows]
        
        return jsonify({
            "success": True,
            "count": len(results),
            "execution_time_ms": round(exec_time, 2),
            "data": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cluster.shutdown()


@app.route('/logs/by-date', methods=['POST'])
def get_logs_by_date():
    """
    Récupère les logs par date
    Body: {"date": "2025-10-15"}
    """
    data = request.json
    date = data.get('date')
    
    if not date:
        return jsonify({"error": "Date required"}), 400
    
    cluster, session = get_session()
    try:
        start = time.time()
        rows = list(session.execute(
            "SELECT * FROM logs_by_date WHERE event_date = %s",
            [date]
        ))
        exec_time = (time.time() - start) * 1000
        
        results = [dict(row._asdict()) for row in rows]
        
        return jsonify({
            "success": True,
            "count": len(results),
            "execution_time_ms": round(exec_time, 2),
            "data": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cluster.shutdown()


@app.route('/tables', methods=['GET'])
def list_tables():
    """Liste toutes les tables du keyspace"""
    cluster, session = get_session()
    try:
        rows = session.execute(
            "SELECT table_name FROM system_schema.tables WHERE keyspace_name = 'nosql_tp'"
        )
        tables = [row.table_name for row in rows]
        return jsonify({"tables": tables})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cluster.shutdown()


@app.route('/logs/latest/<int:user_id>', methods=['GET'])
def get_latest_logs(user_id):
    """
    TÂCHE 2 : Récupère les 100 derniers logs d'un utilisateur
    Optimisé pour Cassandra (clé de partition + clustering)
    """
    limit = request.args.get('limit', 100, type=int)
    
    cluster, session = get_session()
    try:
        start = time.time()
        rows = list(session.execute(
            f"SELECT * FROM logs_by_user WHERE user_id = {user_id} LIMIT {limit}"
        ))
        exec_time = (time.time() - start) * 1000
        
        results = [dict(row._asdict()) for row in rows]
        
        return jsonify({
            "success": True,
            "count": len(results),
            "execution_time_ms": round(exec_time, 2),
            "data": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cluster.shutdown()


@app.route('/logs/aggregate', methods=['POST'])
def aggregate_logs():
    """
    TÂCHE 3 : Agrégation - calcul de moyenne par event_type
    Body: {"event_types": ["PURCHASE", "ADD_TO_CART"], "field": "session_duration_ms"}
    """
    data = request.json
    event_types = data.get('event_types', [])
    field = data.get('field', 'session_duration_ms')
    
    cluster, session = get_session()
    try:
        start = time.time()
        results = {}
        
        for event_type in event_types:
            rows = list(session.execute(
                f"SELECT {field} FROM logs_by_user WHERE event_type = '{event_type}' ALLOW FILTERING"
            ))
            
            if rows:
                values = [getattr(r, field) for r in rows if getattr(r, field) is not None]
                avg_value = sum(values) / len(values) if values else 0
                results[event_type] = {
                    "count": len(rows),
                    "average": round(avg_value, 2),
                    "sum": sum(values),
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0
                }
            else:
                results[event_type] = {"count": 0, "average": 0}
        
        exec_time = (time.time() - start) * 1000
        
        return jsonify({
            "success": True,
            "execution_time_ms": round(exec_time, 2),
            "aggregations": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cluster.shutdown()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
