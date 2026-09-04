# Avasar — Backend

FastAPI backend for the Avasar government-scheme chatbot.

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS / Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start dev server
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /api/health | Health check |

API docs: http://localhost:8000/docs

## Structure

```
app/
├── main.py        # FastAPI application entry point, CORS config, .env loading
├── api/           # Route handlers (future)
├── services/      # Business logic — RAG, LLM, translation (future)
├── models/        # Pydantic request/response schemas (future)
└── core/          # Config, settings, shared utilities (future)
```

## Environment Variables

The backend loads `.env` from the **project root** (one level above `backend/`)
automatically via `python-dotenv` at startup.

Copy `../.env.example` to `../.env` and fill in required values.

Key variables:

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Groq LLM API key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins |
| `EMBEDDING_MODEL` | Sentence Transformer model name for multilingual RAG |
| `VECTOR_STORE_PATH` | Path to FAISS index file |
