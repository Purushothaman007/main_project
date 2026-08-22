from fastapi import APIRouter
from app.schemas.health import HealthResponse, ExecutionHealthResponse
from app.services.docker_service import docker_service

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def get_health():
    return HealthResponse(status="healthy")

@router.get("/health/execution", response_model=ExecutionHealthResponse, tags=["Health"])
async def get_execution_health():
    reachable = docker_service.is_reachable()
    images = docker_service.check_images_exist([
        "college-code-python:3.11",
        "college-code-java:17",
        "college-code-cpp:gcc"
    ])
    system_status = "healthy" if reachable else "unhealthy"
    return ExecutionHealthResponse(
        status=system_status,
        docker_reachable=reachable,
        images={
            "python": images.get("college-code-python:3.11", False),
            "java": images.get("college-code-java:17", False),
            "cpp": images.get("college-code-cpp:gcc", False)
        }
    )
