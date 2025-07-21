# Makefile for fin-qdrant-rag

# It prevents conflicts if a file with the same name
.PHONY: up down test lint format setup env-setup up-detached run-local spacy-model setup

# Setup commands
setup:
	chmod +x scripts/check_setup.sh
	./scripts/check_setup.sh
	uv venv --python 3.11
	poetry run python -m ensurepip --upgrade || true
	poetry install
	make spacy-model
	cp .env.example .env

env-setup:
	cp .env.example .env

# Docker commands
up:
	docker compose --env-file .env -f docker/docker-compose.yml up --build

up-detached:
	docker compose --env-file .env -f docker/docker-compose.yml up -d --build

down:
	docker compose -f docker/docker-compose.yml down

# Local development
run-local:
	poetry run uvicorn src.main:app --reload --host ${FASTAPI_HOST:-0.0.0.0} --port ${FASTAPI_PORT:-8000}

# Testing and quality
test:
	PYTHONPATH=src pytest src/tests -v

spacy-model:
	poetry run python -m spacy download en_core_web_sm
