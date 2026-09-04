from fastapi import APIRouter, HTTPException, status
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about government schemes",
    description="Accepts a citizen query, language code, and optional conversation ID.",
    responses={
        status.HTTP_501_NOT_IMPLEMENTED: {
            "description": "Chat pipeline is not yet implemented",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Chat pipeline is not implemented yet. Architecture ready for RAG and LLM integration."
                    }
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation Error (e.g. missing or empty message)"
        },
    },
)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint for government scheme queries.

    Validates request payload via Pydantic model. Returns HTTP 501 Not Implemented
    until the RAG, LLM, and translation services are plugged in.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Chat pipeline is not implemented yet. Architecture ready for RAG and LLM integration.",
    )
