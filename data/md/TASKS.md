# Project Tasks for fin-qdrant-rag

## 1. Chatbot API (TDD & Clean Code)
- [X] Initial Setup: poetry, dependencies, root endpoint
- [X] Write test for root endpoint (TDD)
- [X] Implement root endpoint to pass test
- [X] Add Pydantic models for chat requests/responses (test model validation)
- [X] Implement /chat endpoint (start with test for dummy response)
- [X] Implement /chat logic to pass tests
- [X] Refactor, document, and review code

## 2. Persistence Layer (TDD & Clean Code)
- [X] Write SQLAlchemy models for chat (chat.py) with test coverage
- [X] Add logs
- [X] Add PostgreSQL service to docker-compose.yml & establish connection (test connection)
- [X] Create .env.example and document required variables
- [X] Write tests for chat message persistence (CRUD)
- [X] Implement persistence logic to pass tests
- [X] Add OpenAI response with Short Memory (Redis) & Long Memory (Qdrant)
- [X] Implement Hybrid Memory Manager with Strategy Pattern
- [X] Add Qdrant service to docker-compose.yml
- [X] Refactor, document, and review code

## 3. RAG Pipeline (PDF Ingestion, TDD)
- [X] Write test for PDF upload endpoint (/upload)
- [X] Implement /upload endpoint to pass test
- [X] Write tests for PDF parsing and chunking (core/utils/parser.py)
- [X] Implement parsing/chunking logic to pass tests
- [X] Write tests for embedding with OpenAI (core/utils/embedding.py)
- [X] Implement embedding logic to pass tests
- [X] Write tests for storing embeddings in Qdrant (core/qdrant_client.py)
- [X] Implement Qdrant storage logic to pass tests
- [X] Refactor, document, and review code

## 4. RAG Chatbot (TDD)
- [X] Write test for /chat endpoint using Qdrant retrieval
- [X] Implement retrieval and prompt construction logic to pass tests
- [X] Write test for OpenAI final response integration
- [X] Implement OpenAI call to pass test
- [X] Refactor, document, and review code

## 5. Dynamic Data Pipeline (TDD)
- [ ] Write tests for news/stocks ingestion pipeline (features/services/dynamic_ingest.py)
- [ ] Implement ingestion logic to pass tests
- [ ] Write tests for periodic scheduling (features/services/scheduler.py)
- [ ] Implement scheduler logic to pass tests
- [ ] Write tests for storing news/stocks in Qdrant (news_feed)
- [ ] Implement Qdrant storage logic to pass tests
- [ ] Refactor, document, and review code

## 6. Dockerization & Environment (TDD)
- [X] Write Dockerfile for API & ingestion pipeline (test build/run)
- [X] Write docker-compose.yml for API, ingestion, Qdrant, PostgreSQL (test integration)
- [X] Add tests for Dockerized setup (health checks, integration)
- [X] Add config.py for settings management (test config loading)
- [x] Refactor, document, and review code

## 7. Engineering Best Practices
- [ ] Enforce code style and linting (e.g., black, isort, flake8)
- [ ] Set up pre-commit hooks
- [ ] Add type hints and mypy checks
- [X] Write and maintain documentation (README, docstrings)
- [ ] Code review for all major features

## 8. Future Considerations (optional)
- [X] Add chat UI (optional)
- [ ] Add CI & CD on AWS
- [ ] Add authentication (optional)
- [ ] Add batch management (optional)


---

**Approach:**
- Write tests first (TDD) for every feature and refactor as needed
- Keep tasks small, focused, and incremental
- Prioritize code readability, maintainability, and documentation
- Review and clean up code after each major step
---

