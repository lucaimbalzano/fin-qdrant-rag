
```sh
fin-qdrant-rag/
│
├── src/
│   ├── core/
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── embedding.py
│   │   │   └── parser.py
│   │   ├── qdrant_client.py
│   │   ├── openai_client.py
│   │   ├── redis_memory_manager.py
│   │   ├── memory_manager.py
│   │   ├── memory_strategy.py
│   │   ├── hybrid_memory_manager.py
│   │   ├── stock_assistant_config.py
│   │   └── logging/
│   │       └── config.py
│   │
│   ├── features/
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   └── upload.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── chat_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── ingestion_service.py
│   │   │   ├── static_ingest.py
│   │   │   ├── dynamic_ingest.py
│   │   │   └── scheduler.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── pydantic/
│   │       │   ├── __init__.py
│   │       │   ├── chat.py
│   │       │   ├── memory.py
│   │       │   └── upload.py
│   │       ├── sqlalchemy/
│   │       │   ├── __init__.py
│   │       │   ├── chat.py
│   │       │   └── upload.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── pg_connection.py
│   │   └── redis_connection.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_chat_endpoint.py
│   │   ├── test_rag_integration.py
│   │   ├── test_redis_memory.py
│   │   ├── test_pydantic_chat.py
│   │   ├── test_pg_connection.py
│   │   ├── test_main.py
│   │   ├── test_qdrant_client.py
│   │   ├── test_upload_endpoint.py
│   │   ├── test_embedding.py
│   │   └── test_pdf_parser.py
│   ├── main.py
│   ├── config.py
│   └── logs/
│
├── data/
│   ├── uploads/
│   ├── test/
│   │   └── test_01.pdf
│   ├── default_knowledge_base/
│   │   └── some_X.pdf
│   │   └── ...
│   └── md/
│       ├── FOLDER_STRUCTURE.md
│       ├── MEMORY_SYSTEM_DESIGN.md
│       ├── PROJECT_PLAN.md
│       └── TASKS.md
├── scripts/
│   ├── create_tables.py
│   └── logs/
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.ingest
│   └── docker-compose.yml
├── logs/
├── .env.example
├── pyproject.toml
├── poetry.lock
├── Makefile
├── README.md
└── .gitignore
```

Legend:
✅ = Implemented and working
⚠️ = Partially implemented, skeleton, or empty file
❌ = Missing/Not implemented