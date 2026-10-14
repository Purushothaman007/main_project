from fastapi import APIRouter, Request, HTTPException
from app.schemas.hint import HintRequest, HintResponse
from app.services.hint_service import generate_hint
from app.core.logging_config import logger

router = APIRouter(prefix="/api/ai", tags=["AI Hints"])


@router.post("/hints", response_model=HintResponse)
async def get_hint(request: Request, body: HintRequest):
    """
    Generate a progressive programming hint using the Gemini API.

    The request must include the student's current code, their message,
    and the desired hint level (1=conceptual, 2=algorithmic, 3=targeted).
    Execution containers are never involved — this is purely AI-driven.
    """
    # Use client IP as the rate-limit key
    client_key = request.client.host if request.client else "anonymous"

    try:
        hint = generate_hint(req=body, client_key=client_key)
        return hint
    except ValueError as e:
        # Rate limit or validation error — return 429
        raise HTTPException(status_code=429, detail=str(e))
    except RuntimeError as e:
        # API key not set, SDK missing, or Gemini error
        logger.error(f"[HintsRoute] RuntimeError: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"[HintsRoute] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error generating hint.")
