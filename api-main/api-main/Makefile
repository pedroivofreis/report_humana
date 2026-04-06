.PHONY: help install install-dev format lint type-check test clean run migrate docker-build docker-up docker-down docker-logs docker-restart docker-clean

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala as dependências de produção
	pip install -r requirements.txt

install-dev: ## Instala as dependências de desenvolvimento
	pip install -r requirements-dev.txt

format: ## Formata o código com black e isort
	./venv/bin/black .
	./venv/bin/isort .

lint: ## Executa linters (ruff e flake8)
	./venv/bin/ruff check .
	./venv/bin/flake8 .

type-check: ## Verifica tipos com mypy
	./venv/bin/mypy app/

test: ## Executa os testes
	./venv/bin/pytest tests/ -v

test-cov: ## Executa os testes com cobertura
	./venv/bin/pytest tests/ -v --cov=app --cov-report=html --cov-report=term

clean: ## Remove arquivos temporários e cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.db" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

run: ## Inicia o servidor de desenvolvimento
	uvicorn main:app --reload --host 0.0.0.0 --port 8001

migrate: ## Executa as migrações do banco de dados
	alembic upgrade head

migrate-create: ## Cria uma nova migração (use NAME=nome_da_migracao)
	alembic revision --autogenerate -m "$(NAME)"

migrate-rollback: ## Reverte a última migração
	alembic downgrade -1

db-reset: ## Reseta o banco de dados (apaga e recria todas as tabelas)
	python scripts/reset_database.py

db-seed: ## Popula o banco com dados de teste (use USERS=50 para definir quantidade)
	python scripts/seed_database.py --users $(or $(USERS),50) --truncate

db-reset-seed: db-reset db-seed ## Reseta e popula o banco de dados

check: format lint type-check ## Executa formatação, linting e verificação de tipos


all: clean install-dev check test ## Executa limpeza, instalação, verificações e testes

# ==================== Docker Commands ====================

docker-build: ## Constrói as imagens Docker
	docker-compose build

docker-up: ## Inicia os containers em modo detached
	docker-compose up -d

docker-up-build: ## Constrói e inicia os containers
	docker-compose up -d --build

docker-start: ## Inicia os containers (sem logs)
	docker-compose start

docker-stop: ## Para os containers sem removê-los
	docker-compose stop

docker-down: ## Para e remove os containers
	docker-compose down

docker-down-volumes: ## Para e remove os containers e volumes (CUIDADO: apaga dados!)
	docker-compose down -v

docker-logs: ## Mostra os logs de todos os serviços
	docker-compose logs -f

docker-logs-api: ## Mostra os logs da API
	docker-compose logs -f api

docker-logs-db: ## Mostra os logs do banco de dados
	docker-compose logs -f postgres

docker-restart: ## Reinicia todos os containers
	docker-compose restart

docker-restart-api: ## Reinicia apenas o container da API
	docker-compose restart api

docker-ps: ## Mostra o status dos containers
	docker-compose ps

docker-exec-api: ## Acessa o shell do container da API
	docker-compose exec api bash

docker-exec-db: ## Acessa o PostgreSQL
	docker-compose exec postgres psql -U postgres -d places_db

docker-migrate: ## Executa as migrações no container
	docker-compose exec api alembic upgrade head

docker-migrate-create: ## Cria uma nova migração no container (use NAME=nome_da_migracao)
	docker-compose exec api alembic revision --autogenerate -m "$(NAME)"

docker-clean: ## Remove todos os containers, imagens e volumes
	docker-compose down -v --rmi all
	docker system prune -f

docker-dev: docker-up-build docker-logs ## Inicia o ambiente de desenvolvimento completo

docker-test: ## Executa os testes no container
	docker-compose exec api pytest tests/ -v
