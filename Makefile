# ============================================================================
# Makefile - TP NoSQL (Cassandra, MongoDB, Elasticsearch)
# ============================================================================

.PHONY: help setup venv install docker-up docker-down docker-build docker-logs \
        clean clean-all test task1 task2 task3 all-tasks api frontend shell \
        data-generate data-insert dev

# Variables
PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTHON_VENV := $(VENV_BIN)/python
DOCKER_COMPOSE := docker-compose

# Couleurs pour l'affichage
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

# ============================================================================
# AIDE
# ============================================================================

help: ## Affiche cette aide
	@echo "$(BLUE)============================================================================$(NC)"
	@echo "$(BLUE)                    TP NoSQL - Makefile                                    $(NC)"
	@echo "$(BLUE)============================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:$(NC) make [target]"
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(setup|venv|install|clean)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(docker|n8n|api)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Tâches:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(task|data)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Autres:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -vE '(setup|venv|install|clean|docker|n8n|api|task|data)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

# ============================================================================
# SETUP & INSTALLATION
# ============================================================================

setup: venv install ## Setup complet (venv + dépendances)
	@echo "$(GREEN)✅ Setup terminé!$(NC)"
	@echo ""
	@echo "$(YELLOW)Pour activer le venv:$(NC)"
	@echo "  source $(VENV)/bin/activate"
	@echo ""
	@echo "$(YELLOW)Pour démarrer Docker:$(NC)"
	@echo "  make docker-up"

venv: ## Crée l'environnement virtuel Python
	@echo "$(BLUE)📦 Création du venv...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@echo "$(GREEN)✅ venv créé dans $(VENV)/$(NC)"

install: $(VENV) ## Installe les dépendances Python
	@echo "$(BLUE)📦 Installation des dépendances...$(NC)"
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dépendances installées$(NC)"

$(VENV):
	@$(MAKE) venv

# ============================================================================
# DOCKER
# ============================================================================

docker-up: ## Démarre tous les services Docker
	@echo "$(BLUE)🐳 Démarrage des services Docker...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Services démarrés$(NC)"
	@echo ""
	@echo "$(YELLOW)Services disponibles:$(NC)"
	@echo "  - Frontend:       http://localhost:3000"
	@echo "  - API:            http://localhost:5050"
	@echo "  - Cassandra:      localhost:9042"
	@echo "  - MongoDB:        localhost:27017"
	@echo "  - Mongo Express:  http://localhost:8081"
	@echo "  - Elasticsearch:  http://localhost:9200"
	@echo "  - Kibana:         http://localhost:5601"

docker-down: ## Arrête tous les services Docker
	@echo "$(BLUE)🐳 Arrêt des services Docker...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Services arrêtés$(NC)"

docker-build: ## Rebuild les images Docker
	@echo "$(BLUE)🐳 Rebuild des images Docker...$(NC)"
	@$(DOCKER_COMPOSE) up -d --build
	@echo "$(GREEN)✅ Images reconstruites et services démarrés$(NC)"

docker-logs: ## Affiche les logs Docker
	@$(DOCKER_COMPOSE) logs -f

docker-status: ## Affiche le statut des containers
	@$(DOCKER_COMPOSE) ps

docker-clean: ## Supprime les volumes Docker (⚠️ données perdues)
	@echo "$(RED)⚠️  Suppression des volumes Docker...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)✅ Volumes supprimés$(NC)"

# ============================================================================
# SERVICES INDIVIDUELS
# ============================================================================

frontend: ## Démarre le frontend React
	@echo "$(BLUE)🔄 Démarrage du frontend...$(NC)"
	@$(DOCKER_COMPOSE) up -d frontend
	@echo "$(GREEN)✅ Frontend disponible sur http://localhost:3000$(NC)"

frontend-dev: ## Lance le frontend en mode développement
	@echo "$(BLUE)🔄 Démarrage du frontend en mode dev...$(NC)"
	@cd frontend && npm run dev

api: ## Démarre l'API backend
	@echo "$(BLUE)🔄 Démarrage de l'API...$(NC)"
	@$(DOCKER_COMPOSE) up -d api
	@echo "$(GREEN)✅ API disponible sur http://localhost:5050$(NC)"

# ============================================================================
# TÂCHES
# ============================================================================

task1: $(VENV) ## Exécute la Tâche 1 (Recherche Full-Text)
	@echo "$(BLUE)🔍 Exécution Tâche 1 - Recherche Full-Text$(NC)"
	@$(DOCKER_COMPOSE) run --rm python-app python /app/scripts/task/task1_simple.py

task2: $(VENV) ## Exécute la Tâche 2 (Accès Ciblé)
	@echo "$(BLUE)👤 Exécution Tâche 2 - Accès Ciblé$(NC)"
	@$(DOCKER_COMPOSE) run --rm python-app python /app/scripts/task/task2_simple.py

task3: $(VENV) ## Exécute la Tâche 3 (Agrégation)
	@echo "$(BLUE)📊 Exécution Tâche 3 - Agrégation$(NC)"
	@$(DOCKER_COMPOSE) run --rm python-app python /app/scripts/task/task3_simple.py

all-tasks: task1 task2 task3 ## Exécute toutes les tâches

# ============================================================================
# DONNÉES
# ============================================================================

data-generate: $(VENV) ## Génère les données de test
	@echo "$(BLUE)📝 Génération des données...$(NC)"
	@$(DOCKER_COMPOSE) run --rm python-app python /app/scripts/data/generate_data.py
	@echo "$(GREEN)✅ Données générées$(NC)"

data-insert: $(VENV) ## Insère les données dans toutes les bases
	@echo "$(BLUE)📥 Insertion des données...$(NC)"
	@$(DOCKER_COMPOSE) run --rm python-app python /app/scripts/insert/cassandra-insert.py
	@$(DOCKER_COMPOSE) run --rm python-app python /app/scripts/insert/mongo_insert.py
	@$(DOCKER_COMPOSE) run --rm python-app python /app/scripts/insert/elasticsearch_insert.py
	@echo "$(GREEN)✅ Données insérées$(NC)"

# ============================================================================
# UTILITAIRES
# ============================================================================

shell: ## Ouvre un shell dans le container Python
	@$(DOCKER_COMPOSE) run --rm python-app /bin/bash

shell-cassandra: ## Ouvre cqlsh dans Cassandra
	@docker exec -it cassandra-db cqlsh

shell-mongo: ## Ouvre mongosh dans MongoDB
	@docker exec -it mongo-db mongosh

test-api: ## Teste l'API
	@echo "$(BLUE)🧪 Test de l'API...$(NC)"
	@curl -s http://localhost:5050/api/health | jq . || echo "$(RED)❌ API non disponible$(NC)"

# ============================================================================
# NETTOYAGE
# ============================================================================

clean: ## Supprime le venv et les fichiers cache
	@echo "$(BLUE)🧹 Nettoyage...$(NC)"
	@rm -rf $(VENV)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

clean-all: clean docker-clean ## Supprime tout (venv + volumes Docker)
	@echo "$(GREEN)✅ Nettoyage complet terminé$(NC)"

# ============================================================================
# WORKFLOW COMPLET
# ============================================================================

wait-healthy: ## Attend que les bases de données soient prêtes
	@echo "$(BLUE)⏳ Attente que les bases soient healthy...$(NC)"
	@timeout=120; \
	while [ $$timeout -gt 0 ]; do \
		if docker exec cassandra-db cqlsh -e "describe keyspaces" >/dev/null 2>&1 && \
		   docker exec mongo-db mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1 && \
		   curl -s http://localhost:9200/_cluster/health >/dev/null 2>&1; then \
			echo "$(GREEN)✅ Toutes les bases sont prêtes!$(NC)"; \
			break; \
		fi; \
		echo "  Attente... ($$timeout s restantes)"; \
		sleep 5; \
		timeout=$$((timeout - 5)); \
	done; \
	if [ $$timeout -le 0 ]; then \
		echo "$(RED)❌ Timeout: les bases ne sont pas prêtes$(NC)"; \
		exit 1; \
	fi

init: ## 🚀 Initialisation complète du projet (une seule commande!)
	@echo ""
	@echo "$(BLUE)============================================================================$(NC)"
	@echo "$(BLUE)     🚀 INITIALISATION COMPLÈTE DU PROJET TP NoSQL                         $(NC)"
	@echo "$(BLUE)============================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Étape 1/5:$(NC) Création du venv Python..."
	@$(MAKE) venv --no-print-directory
	@echo ""
	@echo "$(YELLOW)Étape 2/5:$(NC) Installation des dépendances..."
	@$(MAKE) install --no-print-directory
	@echo ""
	@echo "$(YELLOW)Étape 3/5:$(NC) Build et démarrage de Docker..."
	@$(MAKE) docker-build --no-print-directory
	@echo ""
	@echo "$(YELLOW)Étape 4/5:$(NC) Attente des bases de données..."
	@$(MAKE) wait-healthy --no-print-directory
	@echo ""
	@echo "$(YELLOW)Étape 5/5:$(NC) Génération et insertion des données..."
	@$(MAKE) data-generate --no-print-directory
	@$(MAKE) data-insert --no-print-directory
	@echo ""
	@echo "$(GREEN)============================================================================$(NC)"
	@echo "$(GREEN)     ✅ PROJET INITIALISÉ AVEC SUCCÈS!                                     $(NC)"
	@echo "$(GREEN)============================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)🌐 URLs disponibles:$(NC)"
	@echo "  - Dashboard React:  $(BLUE)http://localhost:3000$(NC)"
	@echo "  - API REST:         $(BLUE)http://localhost:5050/api/health$(NC)"
	@echo "  - Mongo Express:    $(BLUE)http://localhost:8081$(NC)"
	@echo "  - Kibana:           $(BLUE)http://localhost:5601$(NC)"
	@echo ""
	@echo "$(YELLOW)📋 Commandes utiles:$(NC)"
	@echo "  - make all-tasks     Exécuter toutes les tâches"
	@echo "  - make docker-logs   Voir les logs Docker"
	@echo "  - make test-api      Tester l'API"
	@echo "  - make help          Voir toutes les commandes"
	@echo ""

reinit: docker-clean init ## Réinitialise tout (supprime les données et recommence)
	@echo "$(GREEN)✅ Réinitialisation complète terminée$(NC)"
