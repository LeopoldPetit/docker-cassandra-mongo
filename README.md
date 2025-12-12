# TP NoSQL - Comparaison Cassandra, MongoDB, Elasticsearch

Ce projet compare les performances de 3 SGBD NoSQL pour différents cas d'usage avec des logs e-commerce. Il inclut un **dashboard React** interactif pour visualiser les résultats en temps réel.

![Dashboard Preview](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?logo=react)
![API](https://img.shields.io/badge/API-Flask%20Python-green?logo=flask)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

## 🎯 Fonctionnalités

- **Dashboard React** : Interface moderne pour exécuter les tâches et voir les résultats
- **3 Tâches de Benchmark** :
  - 🔍 **Task 1** : Recherche Full-Text (mot "error" dans les logs)
  - 👤 **Task 2** : Accès Ciblé (100 derniers logs d'un utilisateur)
  - 📊 **Task 3** : Agrégation (moyenne session_duration par action)
- **Gestion des données** : Générer/supprimer des logs depuis l'interface
- **Health Check** : Statut en temps réel des 3 bases de données
- **Visualisation** : Graphiques comparatifs avec Recharts

## 📁 Structure du projet

```
test-cassandra/
├── docker-compose.yml          # Stack Docker (8 services)
├── Dockerfile                  # Image Python pour l'API
├── Makefile                    # Automatisation des commandes
├── requirements.txt            # Dépendances Python
├── README.md
├── frontend/                   # Dashboard React
│   ├── Dockerfile              # Image Nginx pour prod
│   ├── nginx.conf              # Configuration proxy
│   ├── package.json
│   └── src/
│       ├── App.tsx             # Composant principal
│       └── components/
│           ├── DataManager.tsx # Gestion des données
│           ├── HealthCheck.tsx # Statut des DBs
│           └── TaskRunner.tsx  # Exécution des tâches
└── scripts/
    ├── api/
    │   └── main_api.py         # API REST Flask (port 5050)
    ├── data/
    │   ├── generate_data.py    # Générateur de logs
    │   └── ecommerce_logs.json # Données générées
    ├── insert/
    │   ├── cassandra-insert.py
    │   ├── mongo_insert.py
    │   └── elasticsearch_insert.py
    └── task/
        ├── task1_simple.py     # Benchmark Full-Text
        ├── task2_simple.py     # Benchmark Accès Ciblé
        └── task3_simple.py     # Benchmark Agrégation
```

## 🚀 Démarrage Rapide

### Option 1 : Une seule commande (recommandé)

```bash
make init
```

Cette commande fait tout automatiquement :
1. ✅ Crée l'environnement Python
2. ✅ Installe les dépendances
3. ✅ Build et démarre Docker
4. ✅ Attend que les bases soient prêtes
5. ✅ Génère et insère les données

### Option 2 : Étape par étape

```bash
# 1. Démarrer les services Docker
docker-compose up -d --build

# 2. Attendre que les bases soient prêtes (~60s)
make wait-healthy

# 3. Générer et insérer les données
make data-generate
make data-insert
```

## 🌐 URLs Disponibles

| Service | URL | Description |
|---------|-----|-------------|
| **🎨 Dashboard React** | http://localhost:3000 | Interface principale |
| **🔌 API REST** | http://localhost:5050/api/health | Backend Flask |
| **📊 Kibana** | http://localhost:5601 | Interface Elasticsearch |
| **🍃 Mongo Express** | http://localhost:8081 | Interface MongoDB |

## 📋 Commandes Makefile

```bash
make help          # Afficher toutes les commandes disponibles

# Setup
make init          # 🚀 Initialisation complète (une seule commande!)
make reinit        # Réinitialiser tout (supprime les données)
make setup         # Créer venv + installer dépendances

# Docker
make docker-up     # Démarrer les services
make docker-down   # Arrêter les services
make docker-build  # Rebuild les images
make docker-logs   # Voir les logs
make docker-clean  # Supprimer les volumes (⚠️ perte de données)

# Tâches
make task1         # Exécuter Task 1 (Full-Text)
make task2         # Exécuter Task 2 (Accès Ciblé)
make task3         # Exécuter Task 3 (Agrégation)
make all-tasks     # Exécuter toutes les tâches

# Données
make data-generate # Générer les logs
make data-insert   # Insérer dans les 3 DBs

# Utilitaires
make test-api      # Tester l'API
make shell         # Shell dans le container Python
make shell-cassandra  # Ouvrir cqlsh
make shell-mongo      # Ouvrir mongosh
```

## 🔌 Endpoints API

L'API REST est disponible sur le port **5050** :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health` | GET | Statut de l'API et des DBs |
| `/api/task/1` | GET | Exécuter Task 1 |
| `/api/task/2` | GET | Exécuter Task 2 |
| `/api/task/3` | GET | Exécuter Task 3 |
| `/api/data/stats` | GET | Statistiques des données |
| `/api/data/generate` | POST | Générer N logs |
| `/api/data/clear` | DELETE | Vider toutes les DBs |

### Exemples curl

```bash
# Vérifier la santé de l'API
curl http://localhost:5050/api/health | jq

# Exécuter Task 1
curl http://localhost:5050/api/task/1 | jq

# Générer 1000 logs
curl -X POST "http://localhost:5050/api/data/generate?count=1000"

# Voir les stats
curl http://localhost:5050/api/data/stats | jq
```

## 🖥️ Accès aux Consoles

### Cassandra (cqlsh)

```bash
make shell-cassandra
# ou
docker exec -it cassandra-db cqlsh
```

```sql
DESCRIBE KEYSPACES;
USE nosql_tp;
SELECT COUNT(*) FROM logs_by_user;
SELECT * FROM logs_by_user WHERE user_id = 10 LIMIT 10;
```

### MongoDB (mongosh)

```bash
make shell-mongo
# ou
docker exec -it mongo-db mongosh
```

```javascript
use nosql_tp
db.logs_ecommerce.countDocuments()
db.logs_ecommerce.find({user_id: 10}).limit(10)
```

### Elasticsearch

```bash
curl http://localhost:9200/ecommerce_logs/_count | jq
curl "http://localhost:9200/ecommerce_logs/_search?size=1" | jq
```

## � Résultats Attendus

| Tâche | Meilleur SGBD | Pourquoi |
|-------|---------------|----------|
| **Full-Text** | 🏆 Elasticsearch | Index inversé optimisé pour la recherche textuelle |
| **Accès Ciblé** | 🏆 Cassandra | Clé de partition + clustering order = accès O(1) |
| **Agrégation** | 🏆 Elasticsearch | Agrégations natives hautement optimisées |

## �️ Technologies

- **Frontend** : React 18, TypeScript, Vite, Recharts, Lucide-React
- **Backend** : Python 3.11, Flask, Flask-CORS
- **Bases de données** :
  - Apache Cassandra 4.1
  - MongoDB 7.0
  - Elasticsearch 8.13.0
- **Infrastructure** : Docker, Docker Compose, Nginx

## 📋 Prérequis

- Docker & Docker Compose
- Make (préinstallé sur macOS avec Xcode Command Line Tools)
- Node.js 18+ (pour le développement frontend uniquement)

## 🐛 Dépannage

### Port 5000 occupé (macOS)

Le port 5000 est utilisé par AirPlay sur macOS. L'API utilise le port **5050** pour éviter ce conflit.

### Cassandra ne démarre pas

```bash
# Vérifier les logs
docker-compose logs cassandra

# Attendre que Cassandra soit prêt
make wait-healthy
```

### Réinitialiser complètement

```bash
make reinit
```
