from fastapi import APIRouter, HTTPException, status
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai_service import ai_service
from app.core.logging_config import logger

router = APIRouter()

@router.post("/ai/chat", response_model=AIChatResponse, tags=["AI Assistant"])
async def ai_chat(request: AIChatRequest) -> AIChatResponse:
    """
    Submits a student prompt, current code context, execution results, and question ID
    to the educational AI programming tutor powered by Google Gemini.
    """
    try:
        return ai_service.generate_tutor_response(request)
    except Exception as e:
        logger.error(f"Unhandled exception in ai_chat endpoint: {e}", exc_info=True)
        return AIChatResponse(
            response="An internal system error occurred while generating AI assistance.",
            is_refusal=False
        )
