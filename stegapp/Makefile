# Makefile pour StegApp

.PHONY: help build up down dev test lint clean install

# Variables
COMPOSE_FILE = docker/docker-compose.yml
BACKEND_DIR = backend
FRONTEND_DIR = frontend

# Aide
help: ## Afficher cette aide
	@echo "StegApp - Commandes disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker
build: ## Construire les images Docker
	docker-compose -f $(COMPOSE_FILE) build

up: ## Démarrer l'application en production
	docker-compose -f $(COMPOSE_FILE) up -d

down: ## Arrêter l'application
	docker-compose -f $(COMPOSE_FILE) down

dev: ## Démarrer en mode développement
	docker-compose -f $(COMPOSE_FILE) --profile dev up

logs: ## Afficher les logs
	docker-compose -f $(COMPOSE_FILE) logs -f

# Développement local
install: ## Installer les dépendances Python
	cd $(BACKEND_DIR) && python -m venv venv
	cd $(BACKEND_DIR) && source venv/bin/activate && pip install -r requirements.txt

# Tests
test: ## Lancer les tests
	cd $(BACKEND_DIR) && python -m pytest tests/ -v

test-cov: ## Lancer les tests avec couverture
	cd $(BACKEND_DIR) && python -m pytest tests/ -v --cov=stego --cov-report=html

# Linting
lint: ## Vérifier le code avec ruff
	cd $(BACKEND_DIR) && ruff check .

lint-fix: ## Corriger automatiquement les erreurs de linting
	cd $(BACKEND_DIR) && ruff check . --fix

# Nettoyage
clean: ## Nettoyer les fichiers temporaires
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf $(BACKEND_DIR)/.pytest_cache
	rm -rf $(BACKEND_DIR)/htmlcov

clean-docker: ## Nettoyer les images Docker
	docker-compose -f $(COMPOSE_FILE) down --rmi all --volumes --remove-orphans

# API
api-health: ## Vérifier la santé de l'API
	curl -f http://localhost:5000/api/health || echo "API non disponible"

# Base de données (si ajoutée plus tard)
db-migrate: ## Appliquer les migrations de base de données
	@echo "Pas de base de données pour le moment"

# Documentation
docs: ## Générer la documentation
	@echo "Documentation disponible dans README.md"

# Déploiement
deploy: ## Déployer en production (à personnaliser)
	@echo "Déploiement en production - à configurer selon votre infrastructure"

# Sécurité
security-check: ## Vérifier la sécurité
	cd $(BACKEND_DIR) && safety check
	cd $(BACKEND_DIR) && bandit -r .

# Performance
benchmark: ## Tests de performance
	cd $(BACKEND_DIR) && python -m pytest tests/ -k "test_performance" -v

# Backup
backup: ## Sauvegarder les données (si nécessaire)
	@echo "Pas de données persistantes à sauvegarder pour le moment"

# Restore
restore: ## Restaurer les données (si nécessaire)
	@echo "Pas de données persistantes à restaurer pour le moment"
