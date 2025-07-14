# Makefile for fin-qdrant-rag

.PHONY: up down test lint format setup env-setup up-detached run-local

# Setup commands
setup:
	uv venv --python 3.11
	poetry install

env-setup:
	cp .env.example .env

# Docker commands
up:
	docker compose -f docker/docker-compose.yml up --build

up-detached:
	docker compose -f docker/docker-compose.yml up -d --build

down:
	docker compose -f docker/docker-compose.yml down

# Local development
run-local:
	poetry run uvicorn src.main:app --reload --host ${FASTAPI_HOST:-0.0.0.0} --port ${FASTAPI_PORT:-8000}

# Testing and quality
test:
	PYTHONPATH=src pytest src/tests -v

lint:
	poetry run flake8 src

format:
	poetry run black src
