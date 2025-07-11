fin-qdrant-rag/
│
├── src/
│   └── app/
│       ├── core/
│       │   ├── utils/                        # General utilities
│       │   │   └── __init__.py
│       │   ├── qdrant_client.py              # Qdrant client/wrappers
│       │   ├── pdf_parser.py                 # PDF parsing utilities
│       │   └── embedding.py                  # OpenAI embedding logic
│       │
│       ├── features/
│       │   ├── endpoints/
│       │   │   ├── chat.py                   # /chat endpoint logic
│       │   │   └── upload.py                 # /upload endpoint logic
│       │   ├── services/
│       │   │   ├── ingestion_service.py      # Ingestion pipeline logic
│       │   │   ├── static_ingest.py          # Static PDF ingestion
│       │   │   ├── dynamic_ingest.py         # News/stock ingestion
│       │   │   └── scheduler.py              # For periodic jobs (APScheduler)
│       │   └── models/
│       │       ├── chat.py                   # Pydantic models for chat
│       │       ├── upload.py                 # Pydantic models for upload
│       │       └── __init__.py
│       │
│       ├── main.py                           # FastAPI entrypoint
│       └── config.py                         # Project configuration
│
├── data/                                     # Uploaded PDFs, temp files, etc.
├── scripts/                                  # CLI tools, one-off scripts
├── tests/                                    # Unit and integration tests
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.ingest
│   └── docker-compose.yml
├── .env.example
├── pyproject.toml
├── poetry.lock
├── README.md
└── PROJECT_PLAN.md