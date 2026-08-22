from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Standardized Code Execution API"
    API_V1_STR: str = "/api/v1"
    
    # Resource Limits (Section 10)
    CPU_LIMIT: float = Field(default=1.0, description="CPU limit in cores")
    MEMORY_LIMIT: str = Field(default="256m", description="Memory limit (e.g. 256m)")
    MAX_COMPILATION_TIME_SEC: int = Field(default=20, description="Max compilation time in seconds")
    MAX_EXECUTION_TIME_SEC: int = Field(default=5, description="Max execution time in seconds")
    MAX_SOURCE_SIZE_BYTES: int = Field(default=100 * 1024, description="Max source code size in bytes (100KB)")
    MAX_STDIN_SIZE_BYTES: int = Field(default=100 * 1024, description="Max stdin size in bytes (100KB)")
    MAX_STDOUT_SIZE_BYTES: int = Field(default=1 * 1024 * 1024, description="Max stdout size in bytes (1MB)")
    MAX_PIDS: int = Field(default=64, description="Max process limit")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
