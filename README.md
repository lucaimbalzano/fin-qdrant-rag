
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

```
fin-qdrant-rag/
├── src/app/
│   ├── core/
│   ├── features/
│   ├── main.py
│   └── config.py
├── data/
├── scripts/
├── tests/
├── docker/
├── .env.example
├── pyproject.toml
└── README.md
```

---

## 🚀 Quickstart

### 1. Clone the repository
```sh
git clone https://github.com/yourusername/fin-qdrant-rag.git
cd fin-qdrant-rag
```

### 2. Create and activate a virtual environment (recommended: uv + Python 3.11+)
```sh
uv venv --python 3.11
source .venv/bin/activate
```

### 3. Install dependencies with Poetry
```sh
poetry install
```

### 4. Run the FastAPI server
```sh
poetry run uvicorn app.main:app --reload --app-dir src
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