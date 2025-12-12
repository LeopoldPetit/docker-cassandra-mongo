# Fichier : cassandra_insert.py

import json
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement
from datetime import datetime
import uuid

# Configuration pour Docker
import os
CONTACT_POINTS = [os.getenv('CASSANDRA_HOST', 'cassandra')]
PORT = int(os.getenv('CASSANDRA_PORT', 9042))
KEYSPACE = "nosql_tp"

# La table est modélisée pour une recherche rapide des logs par utilisateur, triés par timestamp
# Clé primaire : (user_id) est la clé de partition, timestamp est la clé de clustering (tri)
CREATE_TABLE_CQL = f"""
CREATE TABLE IF NOT EXISTS {KEYSPACE}.logs_by_user (
    user_id int,
    timestamp timestamp,
    log_id uuid,
    event_type text,
    product_id text,
    description text,
    session_duration_ms int,
    PRIMARY KEY ((user_id), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
"""

INSERT_CQL = f"""
INSERT INTO {KEYSPACE}.logs_by_user (user_id, timestamp, log_id, event_type, product_id, description, session_duration_ms) 
VALUES (?, ?, ?, ?, ?, ?, ?);
"""

def insert_cassandra():
    print("Connexion à Cassandra...")
    cluster = Cluster(CONTACT_POINTS, port=PORT)
    session = cluster.connect()

    # Créer le keyspace s'il n'existe pas (doit être fait une seule fois)
    session.execute(f"CREATE KEYSPACE IF NOT EXISTS {KEYSPACE} WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}")
    session.set_keyspace(KEYSPACE)

    # Créer la table
    session.execute(CREATE_TABLE_CQL)
    print("Schéma Cassandra créé : table 'logs_by_user'.")

    with open("/app/scripts/ecommerce_logs.json", "r") as f:
        data = json.load(f)

    print(f"Début de l'insertion de {len(data)} lignes (batchs)...")
    
    prepared_stmt = session.prepare(INSERT_CQL)
    batch = BatchStatement()
    batch_size = 100

    for i, log in enumerate(data):
        # Convertir la chaîne ISO vers un objet datetime que Cassandra comprend
        ts = datetime.fromisoformat(log["timestamp"])
        
        # Exclure le produit_id s'il est None (Cassandra n'aime pas les None dans les insertions)
        product_id = log.get("product_id") if log.get("product_id") else None

        batch.add(prepared_stmt, (
            log["user_id"], 
            ts, 
            uuid.UUID(log["log_id"]), 
            log["event_type"], 
            product_id, 
            log["description"], 
            log["session_duration_ms"]
        ))
        
        if (i + 1) % batch_size == 0:
            session.execute(batch)
            batch = BatchStatement()
            print(f"  Insertion de {i+1} / {len(data)} logs...")

    if batch:
        session.execute(batch)

    print("✅ Insertion Cassandra terminée.")
    session.shutdown()
    cluster.shutdown()

if __name__ == "__main__":
    insert_cassandra()
