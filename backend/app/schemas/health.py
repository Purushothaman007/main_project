from typing import Dict
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", json_schema_extra={"example": "healthy"})

class ExecutionHealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    docker_reachable: bool = Field(..., json_schema_extra={"example": True})
    images: Dict[str, bool] = Field(..., json_schema_extra={"example": {"python": True, "java": True, "cpp": True}})
