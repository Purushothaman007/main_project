from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the speaker: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")

class AIChatRequest(BaseModel):
    question_id: str = Field(..., description="ID of the question the student is working on")
    message: str = Field(..., description="Student message or prompt")
    language: str = Field(default="python", description="Programming language selected")
    code: Optional[str] = Field(default="", description="Current student source code")
    execution_output: Optional[str] = Field(default="", description="Latest code execution output/logs")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Recent conversation history")

class AIChatResponse(BaseModel):
    response: str = Field(..., description="AI tutor response message")
    is_refusal: bool = Field(default=False, description="True if a direct solution request was refused")
    action_type: Optional[str] = Field(default=None, description="Optional action identifier (hint, debug, concept, complexity)")
