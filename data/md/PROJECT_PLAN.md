# Project Plan

 
### Overview Project
il sistema prende in input uno o più PDF legati a finanza/trading e permette all'utente di interrogare un agente AI (chatbot) che usa i contenuti indicizzati di questi PDF come contesto.

Tecnologie usate:
- FastAPI (backend API)
- Qdrant (come VectorDB per memorizzare embeddings)
- OpenAI (API chat e embeddings)
- Docker e Docker Compose

Il file `.md` deve contenere:
1. 📁 Struttura delle cartelle e file principali
2. ✅ Checklist step-by-step con sezioni:
   - Setup progetto e Docker
   - Parsing e embedding dei PDF
   - Setup di Qdrant e caricamento vettori
   - Setup di FastAPI con endpoint `/chat` e `/upload`
   - Integrazione con OpenAI API
   - Testing locale e via curl/Postman
   - Considerazioni future (es. autenticazione, UI chat, gestione batch)
3. 📌 Note su file `.env` da creare con chiavi API e configurazioni
4. 🐳 Esempio base di `docker-compose.yml` con tutti i servizi


## 🏗️ Architecture Overview

This project follows a modular, event-driven architecture with two ingestion pipelines and a retriever-augmented generation (RAG) chat service.

### 🔄 Ingestion Pipelines

#### 📚 Pipeline A – Static Knowledge Base (Books, Reports)
- **Input**: PDFs related to trading and finance.
- **Steps**:
  1. Extract text using PyMuPDF or pdfplumber.
  2. Embed each chunk using OpenAI Embedding API.
  3. Store embeddings in Qdrant (Collection: `knowledge_base`).
- **Trigger**: API `/upload` or CLI tool.

#### 📰 Pipeline B – Dynamic Feed (News, Stock Data)
- **Input**: Stock data and news articles (from easy-to-scrape sources).
- **Steps**:
  1. Periodic scraping using cron job or async scheduler (e.g., APScheduler).
  2. Extract text, chunk, embed via OpenAI.
  3. Store in Qdrant (Collection: `news_feed`, possibly with TTL).
- **Trigger**: Automatic via cron or background worker.

---

### 🧠 Chat System – RAG on PDF and News

#### 🛠️ Retrieval-Augmented Generation Pattern
- **User Query → Embedding → Qdrant Search → Prompt OpenAI Chat**
- FastAPI endpoint `/chat`:
  - Accepts question from user.
  - Converts query to embedding.
  - Performs a similarity search in Qdrant.
  - Retrieves top-k chunks from `knowledge_base` + `news_feed`.
  - Constructs a prompt with contextual snippets.
  - Sends final prompt to OpenAI ChatCompletion API and returns the response.

---

### 🧱 Design Patterns Used

- **CQRS (Command Query Responsibility Segregation)**: separate read-heavy (chat) and write-heavy (ingestion) systems.
- **RAG (Retriever-Augmented Generation)**: to give LLMs access to custom vectorized knowledge.
- **ETL Services**: data pipelines separated as services or tasks.
- **Modular Docker Architecture**: each pipeline and FastAPI backend runs in its own container for portability and scalability.

---

### 📦 Data Storage Overview

| Component       | Storage              | Notes                             |
|----------------|----------------------|-----------------------------------|
| PDF Knowledge   | Qdrant (`knowledge_base`) | Static documents                  |
| News/Stocks     | Qdrant (`news_feed`)      | Periodically updated              |
| Metadata        | (Optional) PostgreSQL     | User uploads, tags, project info  |
| Environment     | `.env`                 | API keys and configs               |
| Logs            | Redis or Log Files       | Debugging and task tracking       |

---

This architecture ensures the separation of concerns, allows scalability of the ingestion pipelines, and provides an intelligent and responsive AI chat agent over a rich domain-specific dataset.
