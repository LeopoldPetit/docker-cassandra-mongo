"""
Script principal pour interagir avec Cassandra
"""
import os
from cassandra.cluster import Cluster


def get_cassandra_connection():
    """Établit une connexion avec Cassandra"""
    host = os.getenv('CASSANDRA_HOST', 'localhost')
    port = int(os.getenv('CASSANDRA_PORT', 9042))
    
    print(f"Connexion à Cassandra sur {host}:{port}...")
    
    cluster = Cluster([host], port=port)
    session = cluster.connect()
    
    print("✅ Connexion établie avec succès!")
    return cluster, session


def create_keyspace(session, keyspace_name='test_keyspace'):
    """Crée un keyspace"""
    query = f"""
    CREATE KEYSPACE IF NOT EXISTS {keyspace_name}
    WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
    """
    session.execute(query)
    print(f"✅ Keyspace '{keyspace_name}' créé ou déjà existant")
    return keyspace_name


def create_table(session, keyspace_name):
    """Crée une table exemple"""
    session.set_keyspace(keyspace_name)
    
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY,
        name TEXT,
        email TEXT,
        created_at TIMESTAMP
    )
    """
    session.execute(query)
    print("✅ Table 'users' créée ou déjà existante")


def insert_sample_data(session, keyspace_name):
    """Insère des données exemple"""
    from uuid import uuid4
    from datetime import datetime
    
    session.set_keyspace(keyspace_name)
    
    users = [
        (uuid4(), 'Alice', 'alice@example.com', datetime.now()),
        (uuid4(), 'Bob', 'bob@example.com', datetime.now()),
        (uuid4(), 'Charlie', 'charlie@example.com', datetime.now()),
    ]
    
    query = """
    INSERT INTO users (id, name, email, created_at)
    VALUES (%s, %s, %s, %s)
    """
    
    for user in users:
        session.execute(query, user)
    
    print(f"✅ {len(users)} utilisateurs insérés")


def query_data(session, keyspace_name):
    """Requête les données"""
    session.set_keyspace(keyspace_name)
    
    rows = session.execute("SELECT * FROM users")
    
    print("\n📊 Données dans la table 'users':")
    print("-" * 60)
    for row in rows:
        print(f"  ID: {row.id}")
        print(f"  Nom: {row.name}")
        print(f"  Email: {row.email}")
        print(f"  Créé le: {row.created_at}")
        print("-" * 60)


def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚀 Script Python avec Cassandra")
    print("=" * 60)
    
    cluster = None
    try:
        cluster, session = get_cassandra_connection()
        
        # Créer le keyspace
        keyspace = create_keyspace(session)
        
        # Créer la table
        create_table(session, keyspace)
        
        # Insérer des données
        insert_sample_data(session, keyspace)
        
        # Requêter les données
        query_data(session, keyspace)
        
        print("\n✅ Script terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise
    finally:
        if cluster:
            cluster.shutdown()
            print("🔌 Connexion fermée")


if __name__ == "__main__":
    main()
