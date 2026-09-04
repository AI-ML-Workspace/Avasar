# Avasar — Language Agnostic Chatbot for Government Schemes

> **PS-2 Hackathon Project** | Multilingual RAG-based chatbot for Indian government schemes

---

## Problem Statement

Millions of Indian citizens remain unaware of government welfare schemes due to language barriers and information fragmentation. Avasar bridges this gap with a multilingual conversational AI that can answer questions about government schemes in any Indian language.

---

## Architecture Overview

```
User (any language)
       │
       ▼
┌─────────────┐     REST API      ┌──────────────────────────────┐
│   Frontend  │ ◄───────────────► │   Backend (FastAPI)          │
│  Next.js 15 │                   │  ┌────────────────────────┐  │
│  TypeScript │                   │  │ Language Detection &   │  │
└─────────────┘                   │  │ Translation Layer      │  │
                                  │  ├────────────────────────┤  │
                                  │  │ RAG Pipeline           │  │
                                  │  │  • Sentence Transformers│  │
                                  │  │  • FAISS Vector Store  │  │
                                  │  ├────────────────────────┤  │
                                  │  │ LLM (Groq / Gemini)   │  │
                                  │  └────────────────────────┘  │
                                  └──────────────────────────────┘
                                               │
                                               ▼
                                    ┌─────────────────────┐
                                    │  Knowledge Base      │
                                    │  (Govt. Scheme Docs) │
                                    └─────────────────────┘
```

---

## Folder Responsibilities

| Folder | Owner | Purpose |
|---|---|---|
| `frontend/` | Frontend dev | Next.js 15 + TypeScript UI |
| `backend/` | Backend dev | FastAPI server, RAG pipeline, LLM integration |
| `data/raw/` | Data engineer | Raw government scheme documents (PDFs, JSONs) |
| `data/processed/` | Data engineer | Cleaned, chunked text ready for embedding |
| `vector_store/` | ML engineer | FAISS index files (generated, not committed) |
| `scripts/` | ML engineer | Data ingestion, embedding, index-building scripts |
| `docs/architecture/` | All | Architecture diagrams, ADRs, technical docs |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, TypeScript, App Router |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Embeddings | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (50+ languages) |
| Vector DB | FAISS |
| LLM | Groq API / Google Gemini API |
| Translation | (TBD — langdetect + deep-translator or IndicTrans2) |

---

## Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Git

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on **http://localhost:3000** by default.

---

### Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend runs on **http://localhost:8000**.  
API docs: **http://localhost:8000/docs**  
Health check: `GET http://localhost:8000/api/health`

---

## Environment Variables

**Never commit real secrets.** Copy `.env.example` to `.env` at the project root:

```bash
cp .env.example .env   # Linux / macOS
copy .env.example .env  # Windows
```

The `.env` file is in `.gitignore` and will **never** be committed.

### Frontend vs Backend Variables

| Prefix | Visible to | Example |
|---|---|---|
| `NEXT_PUBLIC_*` | Browser (Next.js) | `NEXT_PUBLIC_API_BASE_URL` |
| All others | Server / Backend only | `GROQ_API_KEY`, `GEMINI_API_KEY` |

> ⚠️ Never place API keys or secrets in `NEXT_PUBLIC_*` variables.

---

## Development Workflow

```
main          ← stable, production-ready
  └─ develop  ← integration branch
       ├─ feature/frontend-*    (frontend devs)
       ├─ feature/backend-*     (backend devs)
       ├─ feature/data-*        (data engineers)
       └─ feature/docs-*        (documentation)
```

1. Branch off `develop` for your feature.
2. Work in your assigned folder to minimize conflicts.
3. Open a PR → `develop` once done.
4. `develop` → `main` before demos / submissions.

---

## Frontend ↔ Backend Communication

Frontend and Backend are **separate applications** that communicate exclusively through **FastAPI REST APIs** over HTTP.  
They are independently deployable and share no code or configuration at this stage.

The Next.js frontend reads `NEXT_PUBLIC_API_BASE_URL` to locate the backend API.

---

## Multilingual Embedding Model

The RAG pipeline uses `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`, which supports 50+ languages including:

- Hindi (hi), Bengali (bn), Tamil (ta), Telugu (te)
- Gujarati (gu), Marathi (mr), Kannada (kn), Malayalam (ml), Punjabi (pa)

The model is configurable via `EMBEDDING_MODEL` in `.env` — no code changes needed to swap models.

---

## Current Status

- [x] Monorepo structure initialized
- [x] Frontend scaffold (Next.js 15 + TypeScript + App Router)
- [x] Backend scaffold (FastAPI + health endpoint)
- [x] Multilingual embedding model configured
- [ ] RAG pipeline
- [ ] Language detection & translation
- [ ] LLM integration
- [ ] Government scheme knowledge base
- [ ] UI implementation
