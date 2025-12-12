# TP NoSQL - Comparaison Cassandra, MongoDB, Elasticsearch

Ce projet compare les performances de 3 SGBD NoSQL pour différents cas d'usage avec des logs e-commerce.

## 📁 Structure du projet

```
test-cassandra/
├── docker-compose.yml          # Stack Docker (5 services)
├── Dockerfile                  # Image Python
├── requirements.txt            # Dépendances Python
├── README.md
└── scripts/
    ├── data/
    │   ├── generate_data.py    # Génère 50k logs e-commerce
    │   └── ecommerce_logs.json # Données générées
    ├── insert/
    │   ├── cassandra-insert.py # Insertion Cassandra
    │   ├── mongo_insert.py     # Insertion MongoDB
    │   └── elasticsearch_insert.py # Insertion Elasticsearch
    └── task/
        ├── task1_simple.py     # Full-text search
        ├── task2_simple.py     # Accès ciblé
        └── task3_simple.py     # Agrégation
```

## 🚀 Démarrage Rapide

### 1. Démarrer tous les services

```bash
docker-compose up -d
```

### 2. Vérifier que tous les services sont prêts

```bash
docker-compose ps
```

### 3. Attendre que Cassandra soit prêt (~30s)

```bash
docker-compose logs -f cassandra
# Attendre "Created default superuser role 'cassandra'"
```

---

## 📊 Commandes du TP

### Générer les données (50 000 logs)

```bash
docker-compose run --rm python-app python scripts/data/generate_data.py
```

### Insérer les données dans les 3 SGBD

```bash
# Cassandra
docker-compose run --rm python-app python scripts/insert/cassandra-insert.py

# MongoDB
docker-compose run --rm python-app python scripts/insert/mongo_insert.py

# Elasticsearch
docker-compose run --rm python-app python scripts/insert/elasticsearch_insert.py
```

### Exécuter les 3 tâches de benchmark

```bash
# Tâche 1 : Recherche Full-Text
docker-compose run --rm python-app python scripts/task/task1_simple.py

# Tâche 2 : Accès Ciblé (user_id=10, 100 derniers logs)
docker-compose run --rm python-app python scripts/task/task2_simple.py

# Tâche 3 : Agrégation (moyenne session_duration_ms)
docker-compose run --rm python-app python scripts/task/task3_simple.py
```

---

## 🔧 Commandes Utiles Docker

### Gestion des services

```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (RESET complet des données)
docker-compose down -v

# Redémarrer un service spécifique
docker-compose restart cassandra
docker-compose restart mongo
docker-compose restart elasticsearch

# Voir les logs en temps réel
docker-compose logs -f
docker-compose logs -f cassandra
docker-compose logs -f mongo
docker-compose logs -f elasticsearch
```

### Reconstruire l'image Python

```bash
docker-compose build python-app
```

---

## 🖥️ Accès aux Consoles

### Cassandra (cqlsh)

```bash
docker-compose exec cassandra cqlsh
```

Commandes CQL utiles :
```sql
-- Lister les keyspaces
DESCRIBE KEYSPACES;

-- Utiliser le keyspace du TP
USE nosql_tp;

-- Voir les tables
DESCRIBE TABLES;

-- Voir le schéma d'une table
DESCRIBE TABLE logs_by_user;

-- Compter les documents
SELECT COUNT(*) FROM logs_by_user;

-- Requête exemple
SELECT * FROM logs_by_user WHERE user_id = 10 LIMIT 10;
```

### MongoDB (mongosh)

```bash
docker-compose exec mongo mongosh
```

Commandes MongoDB utiles :
```javascript
// Utiliser la base du TP
use nosql_tp

// Compter les documents
db.logs_ecommerce.countDocuments()

// Voir les index
db.logs_ecommerce.getIndexes()

// Requête exemple
db.logs_ecommerce.find({user_id: 10}).sort({timestamp: -1}).limit(10)

// Explain d'une requête
db.logs_ecommerce.find({user_id: 10}).explain("executionStats")
```

### Elasticsearch (curl)

```bash
# Depuis le host
curl -X GET "localhost:9200/_cat/indices?v"
curl -X GET "localhost:9200/ecommerce_logs/_count"
curl -X GET "localhost:9200/ecommerce_logs/_search?size=1" | jq
```

---

## 🌐 Interfaces Web

| Service | URL | Description |
|---------|-----|-------------|
| **Kibana** | http://localhost:5601 | Interface Elasticsearch |
| **Mongo Express** | http://localhost:8081 | Interface MongoDB |

---

## 📋 Variables d'Environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `CASSANDRA_HOST` | Hôte Cassandra | cassandra |
| `MONGO_HOST` | Hôte MongoDB | mongo |
| `ES_HOST` | Hôte Elasticsearch | elasticsearch |

---

## 🎯 Résultats Attendus

| Tâche | Meilleur SGBD | Pourquoi |
|-------|---------------|----------|
| **Full-Text** | Elasticsearch | Index inversé optimisé |
| **Accès Ciblé** | Cassandra | Clé de partition + clustering |
| **Agrégation** | Elasticsearch | Agrégations natives optimisées |
