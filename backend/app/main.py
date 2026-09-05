from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.chat import router as chat_router
from app.api.schemes import router as schemes_router

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(chat_router, prefix="/api")
app.include_router(schemes_router, prefix="/api")


@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint — confirms the API server is operational."""
    return {"status": "ok", "service": "avasar-api"}
