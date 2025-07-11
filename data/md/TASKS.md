# Project Tasks for fin-qdrant-rag

## 1. Chatbot API (TDD & Clean Code)
- [X] Initial Setup: poetry, dependencies, root endpoint
- [X] Write test for root endpoint (TDD)
- [X] Implement root endpoint to pass test
- [ ] Implement /chat endpoint (start with test for dummy response)
- [ ] Add Pydantic models for chat requests/responses (test model validation)
- [ ] Implement /chat logic to pass tests
- [ ] Refactor, document, and review code

## 2. Persistence Layer (TDD & Clean Code)
- [ ] Write SQLAlchemy models for chat (chat.py) with test coverage
- [ ] Add PostgreSQL service to docker-compose.yml & establish connection (test connection)
- [ ] Create .env.example and document required variables
- [ ] Add config.py for settings management (test config loading)
- [ ] Write tests for chat message persistence (CRUD)
- [ ] Implement persistence logic to pass tests
- [ ] Refactor, document, and review code

## 3. RAG Pipeline (PDF Ingestion, TDD)
- [ ] Write test for PDF upload endpoint (/upload)
- [ ] Implement /upload endpoint to pass test
- [ ] Write tests for PDF parsing and chunking (core/pdf_parser.py)
- [ ] Implement parsing/chunking logic to pass tests
- [ ] Write tests for embedding with OpenAI (core/embedding.py)
- [ ] Implement embedding logic to pass tests
- [ ] Write tests for storing embeddings in Qdrant (core/qdrant_client.py)
- [ ] Implement Qdrant storage logic to pass tests
- [ ] Refactor, document, and review code

## 4. RAG Chatbot (TDD)
- [ ] Write test for /chat endpoint using Qdrant retrieval
- [ ] Implement retrieval and prompt construction logic to pass tests
- [ ] Write test for OpenAI final response integration
- [ ] Implement OpenAI call to pass test
- [ ] Refactor, document, and review code

## 5. Dynamic Data Pipeline (TDD)
- [ ] Write tests for news/stocks ingestion pipeline (features/services/dynamic_ingest.py)
- [ ] Implement ingestion logic to pass tests
- [ ] Write tests for periodic scheduling (features/services/scheduler.py)
- [ ] Implement scheduler logic to pass tests
- [ ] Write tests for storing news/stocks in Qdrant (news_feed)
- [ ] Implement Qdrant storage logic to pass tests
- [ ] Refactor, document, and review code

## 6. Dockerization & Environment (TDD)
- [ ] Write Dockerfile for API & ingestion pipeline (test build/run)
- [ ] Write docker-compose.yml for API, ingestion, Qdrant, PostgreSQL (test integration)
- [ ] Add tests for Dockerized setup (health checks, integration)
- [ ] Refactor, document, and review code

## 7. Engineering Best Practices
- [ ] Enforce code style and linting (e.g., black, isort, flake8)
- [ ] Set up pre-commit hooks
- [ ] Add type hints and mypy checks
- [ ] Write and maintain documentation (README, docstrings)
- [ ] Code review for all major features

## 8. Future Considerations (optional)
- [ ] Add chat UI (optional)
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

