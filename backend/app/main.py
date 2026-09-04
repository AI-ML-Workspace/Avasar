from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load .env from the project root (one level above backend/)
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(
    title="Avasar API",
    description="Language Agnostic Chatbot for Government Schemes",
    version="0.1.0",
)

# CORS — allow the Next.js dev server during development.
# Set CORS_ORIGINS in .env for production (comma-separated URLs).
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint — confirms the API is running."""
    return {"status": "ok", "service": "avasar-api"}
