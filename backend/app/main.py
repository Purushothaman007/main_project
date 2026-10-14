from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1.health import router as health_router
from app.api.v1.execute import router as execute_router
from app.api.v1.hints import router as hints_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:  initialise the warm container pool (one pool per language image).
              If Docker is unavailable the pool is silently skipped — the
              execution service falls back to on-demand containers automatically.

    Shutdown: drain and remove all idle containers so nothing leaks.
    """
    from app.services.container_pool import pool_registry
    from app.services.docker_service import docker_service
    from app.models.language_config import LANGUAGE_CONFIGS
    from docker.errors import DockerException

    try:
        client = docker_service.client
        pool_registry.initialize(client=client, language_configs=LANGUAGE_CONFIGS)
    except DockerException as e:
        # Docker not running at startup — pool stays empty, on-demand fallback used
        import logging
        logging.getLogger(__name__).warning(
            f"Docker unavailable at startup, warm pool disabled: {e}"
        )

    yield  # application runs here

    pool_registry.shutdown()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Browser-Based Coding Environment API for running code in isolated Docker containers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(execute_router, prefix=settings.API_V1_STR)
app.include_router(hints_router)
