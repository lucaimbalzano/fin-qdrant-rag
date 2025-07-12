
<h1 align="center">fin-qdrant-rag</h1>
<p align="center">A Retrieval-Augmented Generation (RAG) system for finance/trading PDFs using FastAPI, Qdrant, OpenAI, and LangChain.</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=fff&style=for-the-badge" alt="Python Badge">
    <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=fff&style=for-the-badge" alt="FastAPI Badge">
    <img src="https://img.shields.io/badge/Qdrant-20B2AA?logo=qdrant&logoColor=fff&style=for-the-badge" alt="Qdrant Badge">
    <img src="https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=fff&style=for-the-badge" alt="OpenAI Badge">
    <img src="https://img.shields.io/badge/LangChain-000000?logo=langchain&logoColor=fff&style=for-the-badge" alt="LangChain Badge">
    <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff&style=for-the-badge" alt="Docker Badge">
    <img src="https://img.shields.io/badge/Poetry-181717?logo=python&logoColor=fff&style=for-the-badge" alt="Poetry Badge">
</p>

---

## 📖 Project Overview

fin-qdrant-rag is a modular, production-ready backend for building Retrieval-Augmented Generation (RAG) chatbots over finance/trading documents. It ingests PDFs, indexes them with Qdrant, and enables natural language Q&A via OpenAI's LLMs.

---

## 📁 Folder Structure

📋 [View the complete folder structure](./data/md/FOLDER_STRUCTURE.md)

The project follows a modular architecture with clear separation of concerns:

- **`src/core/`** - Core utilities, memory management, and configuration
- **`src/features/`** - Business logic, endpoints, services, and models
- **`src/database/`** - Database connections (PostgreSQL & Redis)
- **`src/tests/`** - Comprehensive test suite
- **`docker/`** - Containerization setup
- **`data/`** - Documentation and static files

📋 [View the complete project plan](./data/md/PROJECT_PLAN.md)

---

## 💠 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Poetry (for dependency management)

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/fin-qdrant-rag.git
cd fin-qdrant-rag

# Setup environment and install dependencies
make setup
```

### 2. Environment Configuration
```bash
# Copy and configure environment variables
make env-setup

# Edit .env with your configuration:
# - OpenAI API key
# - Database credentials  
# - Redis settings
```

### 3. Run with Docker (Recommended)
```bash
# Start all services
make up

# Or run in background
make up-detached
```

### 4. Run Locally (Alternative)
```bash
# Start PostgreSQL and Redis manually, then:
make run-local
```

### 5. Verify Installation
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs




## 💠 Utils

### Run tests
```sh
$ poetry run pytest
or 
$ make test
```

###  Docker
```bash
# build docker-compose and run it
$ docker compose -f docker/docker-compose.yml up --build


# check internal logs
$ docker exec fqr_proj_api cat logs/api.log
$ docker exec fqr_proj_api cat logs/database.log
$ docker exec fqr_proj_api cat logs/app.log

# check tables
$ docker exec -it fqr_proj_postgresdb psql -U $POSTGRES_USER -d $POSTGRES_DB -c '\dt'
# check chat_messages
$ docker exec -it fqr_proj_postgresdb psql -U postgres -d fqr_db -c 'SELECT * FROM chat_messages;'

            
```


### Curls examples
```
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"user_message": "hello world"}' | jq
```

### Redis
```bash
# Check memory infos
$ docker exec fqr_proj_redis redis-cli info memory

# Check Keys stored
$ docker exec fqr_proj_redis redis-cli keys "*"

# Check Size and Content conversion key
$ docker exec fqr_proj_redis redis-cli llen conversation:default_user
(Get all elements of the list from the first element to the last one) 
$ docker exec fqr_proj_redis redis-cli lrange conversation:default_user 0 -1

# Check Database Stats
$ docker exec fqr_proj_redis redis-cli info keyspace

# Clear all data
$ docker exec fqr_proj_redis redis-cli flushall
```

Visit [http://localhost:8000](http://localhost:8000) to check the root endpoint.

---

## 🛠️ Tech Stack
- Python 3.11+
- FastAPI
- Qdrant
- OpenAI API
- LangChain
- Poetry
- Docker

---

## 📄 License
MIT @lucaimbalzano