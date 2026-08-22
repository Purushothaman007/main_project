from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class ExecutionStatus(str, Enum):
    COMPLETED = "COMPLETED"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    OUTPUT_LIMIT_EXCEEDED = "OUTPUT_LIMIT_EXCEEDED"
    SYSTEM_ERROR = "SYSTEM_ERROR"

class ExecutionRequest(BaseModel):
    language: str = Field(..., description="Target programming language (python, java, cpp)", json_schema_extra={"example": "python"})
    code: str = Field(..., description="Source code string to execute", json_schema_extra={"example": "print('Hello World')"})
    stdin: Optional[str] = Field(default="", description="Standard input string", json_schema_extra={"example": ""})

class ExecutionResponse(BaseModel):
    success: bool = Field(..., description="True if program executed and exited zero with no limit violations")
    language: str = Field(..., description="Language used for execution")
    stdout: str = Field(..., description="Captured standard output")
    stderr: str = Field(..., description="Captured standard error")
    exit_code: int = Field(..., description="Process exit code")
    execution_time_ms: int = Field(..., description="Execution wall-clock time in milliseconds")
    status: ExecutionStatus = Field(..., description="Overall execution status classification")
    execution_id: str = Field(..., description="Unique tracking ID for this execution")
