from enum import Enum
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class HintLevel(int, Enum):
    CONCEPTUAL = 1   # guiding question, relevant concept
    ALGORITHMIC = 2  # approach or data structure suggestion
    TARGETED = 3     # partial pseudocode or focused guidance


class HintType(str, Enum):
    CONCEPTUAL = "conceptual"
    ALGORITHMIC = "algorithmic"
    TARGETED = "targeted"
    DEBUGGING = "debugging"


class ConversationMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class HintRequest(BaseModel):
    provider: Literal["gemini", "groq"] = Field(default="gemini")
    language: str = Field(..., description="python | java | cpp")
    source_code: str = Field(default="", description="Current student code in the editor")
    hint_level: int = Field(default=1, ge=1, le=3, description="1=conceptual 2=algorithmic 3=targeted")
    student_message: str = Field(..., description="Student's question or message", min_length=1, max_length=1000)
    error_output: Optional[str] = Field(default="", description="Stderr from last execution, if any")
    conversation_history: Optional[List[ConversationMessage]] = Field(
        default=[], description="Last N turns of conversation for context"
    )
    problem_statement: Optional[str] = Field(
        default="",
        description="The problem the student is trying to solve (title + description + examples)",
        max_length=4000,
    )


class HintResponse(BaseModel):
    hint_level: int
    hint_type: str
    message: str
    next_hint_available: bool
