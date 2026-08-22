from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1.health import router as health_router
from app.api.v1.execute import router as execute_router

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Browser-Based Coding Environment API for running code in isolated Docker containers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
