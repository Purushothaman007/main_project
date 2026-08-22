from fastapi import APIRouter, HTTPException, status
from app.schemas.execute import ExecutionRequest, ExecutionResponse, ExecutionStatus
from app.services.execution_service import execution_service
from app.core.logging_config import logger

router = APIRouter()

@router.post("/execute", response_model=ExecutionResponse, tags=["Execution"])
async def execute_code(request: ExecutionRequest) -> ExecutionResponse:
    """
    Submits code snippet for isolated container execution.
    Returns structured execution result containing status, logs, exit code, and execution time.
    """
    try:
        return execution_service.execute_code(request)
    except Exception as e:
        logger.error(f"Unhandled exception in execute_code endpoint: {e}", exc_info=True)
        return ExecutionResponse(
            success=False,
            language=request.language,
            stdout="",
            stderr="An internal system error occurred during execution.",
            exit_code=-1,
            execution_time_ms=0,
            status=ExecutionStatus.SYSTEM_ERROR,
            execution_id="exec_error"
        )
