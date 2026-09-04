# Avasar — Backend

FastAPI backend for the Avasar multilingual government-scheme chatbot.

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point, CORS, router mounting
│   ├── api/
│   │   └── chat.py          # Chat route endpoints (POST /api/chat)
│   ├── models/
│   │   ├── chat.py          # Pydantic schemas (ChatRequest, ChatResponse, SourceItem)
│   │   └── document.py      # Ingestion schemas (SchemeDocument, ProcessedChunk)
│   ├── services/
│   │   ├── chunking.py      # Deterministic text chunking service
│   │   ├── embedding.py     # Multilingual SentenceTransformer embeddings (L2-normalized)
│   │   ├── ingestion.py     # Document loading, normalization, and JSONL saving
│   │   ├── vector_store.py  # FAISS IndexFlatIP store with metadata persistence
│   │   ├── rag.py           # RAG retrieval service (query -> embedding -> vector search)
│   │   ├── llm_providers.py # Provider-agnostic adapters: Groq, Gemini, OpenAI
│   │   ├── llm.py           # Grounded response generation service & prompt templates
│   │   ├── language.py      # Language detection service interface
│   │   └── translation.py   # Translation service interface
│   └── core/
│       └── config.py        # Centralized app configuration & env loading
├── tests/
│   ├── test_ingestion.py    # Unit tests for loading, normalization, and chunking
│   ├── test_vector_store.py # Unit and integration tests for FAISS vector store and RAG
│   └── test_llm.py          # Unit tests for provider adapters, missing keys, and grounding
├── requirements.txt         # Production dependencies
└── README.md                # Backend architecture and API documentation
```

---

## Setup & Running

### 1. Prerequisites
- Python 3.11+
- Virtual environment (`venv`)

### 2. Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Dev Server

```bash
uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`
- Redoc Documentation: `http://localhost:8000/redoc`

---

## Environment Configuration

Configuration is centralized in `app/core/config.py` and loaded from the **project root**:
1. `../../.env` (root baseline)
2. `../../.env.local` (root local override)

> 🔒 **Security**: All API keys (`GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`) remain strictly server-side and are **never** exposed in API responses or to the frontend.

| Variable | Default | Description |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated list of allowed frontend origins |
| `LLM_PROVIDER` | `groq` | Active LLM provider: `groq`, `gemini`, or `openai` |
| `GROQ_API_KEY` | None | API key for Groq |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Model ID for Groq (e.g. `llama-3.3-70b-versatile`, `qwen/qwen3.6-27b`) |
| `GEMINI_API_KEY` | None | API key for Google Gemini |
| `GEMINI_MODEL` | `gemini-flash-latest` | Model ID for Gemini (e.g. `gemini-flash-latest`) |
| `OPENAI_API_KEY` | None | API key for OpenAI (fallback) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model ID for OpenAI |
| `LLM_TEMPERATURE` | `0.1` | Sampling temperature (conservative for factual schemes) |
| `LLM_MAX_TOKENS` | `1024` | Maximum tokens in generated response |
| `VECTOR_STORE_PATH` | `../vector_store/index.faiss` | Path to FAISS vector index |
| `EMBEDDING_MODEL` | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | Multilingual embedding model |
| `DEFAULT_LANGUAGE` | `en` | Fallback language code |

---

## API Contract

### 1. Health Check

- **Method**: `GET`
- **Path**: `/api/health`
- **Status**: `200 OK`

**Response**:
```json
{
  "status": "ok",
  "service": "avasar-api"
}
```

---

### 2. Chat Endpoint

- **Method**: `POST`
- **Path**: `/api/chat`
- **Content-Type**: `application/json`

#### Request Payload (`ChatRequest`)

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | string | **Yes** (min 1 char) | Citizen's query in any Indian language or English |
| `language` | string | No | ISO 639-1 code (e.g. `"hi"`, `"en"`). Auto-detected if omitted. |
| `conversation_id` | string | No | Unique ID to maintain multi-turn chat context |

**Request Example**:
```json
{
  "message": "How do I apply for PM Kisan scheme?",
  "language": "en",
  "conversation_id": "conv_9f82d1c0"
}
```

#### Response Payload (`ChatResponse`)

| Field | Type | Description |
|---|---|---|
| `answer` | string | Generated conversational response explaining the scheme |
| `language` | string | ISO 639-1 language code of the response |
| `sources` | array | List of verified government scheme citations |
| `sources[].title` | string | Name of the government scheme or official document |
| `sources[].url` | string / null | Official portal or document URL |
| `sources[].snippet` | string / null | Excerpt or key eligibility clause cited |
| `sources[].score` | float / null | Vector retrieval relevance score |
| `conversation_id` | string / null | Conversation identifier |

**Response Example (Target)**:
```json
{
  "answer": "PM Kisan Samman Nidhi provides eligible farmer families with ₹6,000 per year distributed in three equal installments of ₹2,000 directly into their bank accounts. Applications can be submitted online via the PM Kisan portal.",
  "language": "en",
  "sources": [
    {
      "title": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
      "url": "https://pmkisan.gov.in/",
      "snippet": "Financial benefit of Rs 6000/- per year in three equal installments to all landholding farmers families.",
      "score": 0.92
    }
  ],
  "conversation_id": "conv_9f82d1c0"
}
```

#### Status Codes & Error Responses

- **`200 OK`**: Successful response (when RAG/LLM pipeline is active).
- **`422 Unprocessable Entity`**: Request validation failed (e.g. missing or empty `message`).
  ```json
  {
    "detail": [
      {
        "type": "string_too_short",
        "loc": ["body", "message"],
        "msg": "String should have at least 1 character"
      }
    ]
  }
  ```
- **`501 Not Implemented`**: Architecture ready, pipeline pending integration.
  ```json
  {
    "detail": "Chat pipeline is not implemented yet. Architecture ready for RAG and LLM integration."
  }
  ```

---

## Service Interfaces

The service layer defines clear boundaries for the upcoming RAG, LLM, translation, and language modules:

- **`RAGService` (`app/services/rag.py`)**: Interface for querying FAISS vector store and retrieving top-k scheme sources.
- **`LLMService` (`app/services/llm.py`)**: Interface for generating grounded answers using Groq or Gemini models.
- **`LanguageService` (`app/services/language.py`)**: Interface for detecting user query language across 22+ Indian languages and English.
- **`TranslationService` (`app/services/translation.py`)**: Interface for translating text between Indic languages and English.

---

## Document Ingestion Pipeline (Phase 2)

The ingestion pipeline converts raw government scheme files from `data/raw/` into clean, retrieval-ready chunks saved in `data/processed/chunks.jsonl`.

### Supported Raw Input Formats
- `.json`: Array of scheme objects or single scheme object with keys: `title`/`scheme_name`, `url`/`link`, `ministry`/`source_name`, `description`, `eligibility`, `benefits`, `application_process`.
- `.jsonl`: Line-delimited JSON objects.
- `.txt` / `.md`: Plain text or Markdown documents.

### Running Ingestion Locally

```bash
# Run with default settings (data/raw -> data/processed/chunks.jsonl)
python scripts/ingest.py

# Run with custom chunk size and overlap
python scripts/ingest.py --chunk-size 600 --chunk-overlap 150

# Run with custom directories
python scripts/ingest.py --raw-dir data/raw --output data/processed/chunks.jsonl
```

### Running Backend Tests

```bash
cd backend
python -m unittest discover tests -v
```

---

## Vector Store & Multilingual Retrieval (Phase 3)

### Index Architecture
- **Embedding Model**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (768-dimensional, 50+ languages).
- **FAISS Index Type**: `faiss.IndexFlatIP` (Exact Inner Product).
  Since vectors are strictly L2-normalized during embedding (`normalize_embeddings=True`), inner product mathematically equals exact cosine similarity.
- **Metadata Persistence**: The index vectors are paired with an associated `index.meta.json` file storing full `ProcessedChunk` records, preserving scheme title, official URL, source name, language, and custom attributes across reloads.

### Building the Vector Store

```bash
# Build FAISS index from data/processed/chunks.jsonl into vector_store/index.faiss
python scripts/build_vector_store.py

# Custom paths
python scripts/build_vector_store.py --chunks-file data/processed/chunks.jsonl --output-index vector_store/index.faiss
```

### Verifying Multilingual Retrieval

```bash
# Run test queries in English, Hindi, and low-relevance topics
python scripts/verify_retrieval.py
```

---

## LLM Service & Grounded Generation (Phase 4)

### Architecture
- **Provider-Agnostic Abstraction**: `LLMProvider` base class with concrete adapters:
  - `GroqProvider` (using official `groq` SDK)
  - `GeminiProvider` (using official `google.genai` SDK)
  - `OpenAIProvider` (using official `openai` SDK)
- **Factory**: `get_llm_provider(provider_name)` dynamically instantiates the configured adapter.
- **Unified Interface**:
  ```python
  provider.generate(system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str
  ```
- **Grounded Answer Service**:
  ```python
  llm_service = LLMService()
  answer = await llm_service.generate_answer(query="...", sources=[SourceItem(...)])
  ```

### Grounding Principles
1. **Strict Context Boundaries**: Answers are formulated strictly from retrieved scheme sources.
2. **Zero Hallucination**: No invented scheme benefits, application rules, or external assumptions.
3. **Transparent Uncertainty**: When retrieved context lacks sufficient information, clearly states: *"Based on the verified government scheme records currently available, there is not enough information to answer this question."*
4. **Detail Preservation**: Exact numbers, eligibility conditions, exclusion criteria, and official portals are preserved.

### Manual Verification Script

```bash
# Verify using default provider (from LLM_PROVIDER in .env)
python scripts/verify_llm.py

# Test specific provider
python scripts/verify_llm.py --provider groq
python scripts/verify_llm.py --provider gemini
python scripts/verify_llm.py --provider openai
```


