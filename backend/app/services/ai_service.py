import re
import logging
from typing import Optional, List
from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.ai import AIChatRequest, AIChatResponse, ChatMessage
from app.services.question_service import question_service

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = (
    "You are an AI programming tutor inside a college programming laboratory.\n"
    "Your purpose is to help students understand programming problems and develop their own solutions.\n"
    "You MUST NEVER provide a complete solution to an assessment problem.\n"
    "You MUST NEVER provide a complete working program that the student can directly submit.\n"
    "You MUST NEVER rewrite the student's entire code into a final correct solution.\n"
    "You may explain concepts, algorithms, data structures, debugging errors, time and space complexity, and provide progressive hints.\n"
    "When the student asks for the complete solution or complete code, refuse briefly and politely, then provide a useful conceptual hint or guiding question instead.\n"
    "Always help the student make progress without doing the entire problem for them.\n"
    "Use the student's current code and execution results when providing debugging guidance.\n"
    "Do not reveal hidden test cases, expected hidden outputs, reference solutions, or grading internals."
)

SOLUTION_REQUEST_PATTERNS = [
    r"give\s+(me\s+)?(the\s+)?(complete\s+|full\s+)?code",
    r"give\s+(me\s+)?(the\s+)?(complete\s+|full\s+)?solution",
    r"solve\s+(this|it)\s+(completely|for\s+me)?",
    r"write\s+(the\s+)?(complete\s+|full\s+)?(code|answer|solution|program|implementation)",
    r"show\s+(me\s+)?(the\s+)?(complete\s+|full\s+)?(program|code|solution)",
    r"give\s+full\s+implementation",
    r"just\s+give\s+(me\s+)?the\s+answer",
    r"write\s+it\s+for\s+me",
]

class AIService:
    def __init__(self):
        self.model_name = "gemini-3.6-flash"

    def _detect_solution_request(self, message: str) -> bool:
        lowered = message.lower()
        for pattern in SOLUTION_REQUEST_PATTERNS:
            if re.search(pattern, lowered):
                return True
        return False

    def generate_tutor_response(self, request: AIChatRequest) -> AIChatResponse:
        # Check API key presence
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.strip() == "":
            return AIChatResponse(
                response=(
                    "⚠️ **Gemini API Key missing.**\n\n"
                    "Please set `GEMINI_API_KEY` in `backend/.env` to enable the AI Programming Tutor."
                ),
                is_refusal=False
            )

        # Retrieve static question context
        question = question_service.get_question_by_id(request.question_id)
        question_context = ""
        if question:
            question_context = (
                f"PROBLEM TITLE: {question.title}\n"
                f"DIFFICULTY: {question.difficulty}\n"
                f"TOPIC: {question.topic}\n"
                f"DESCRIPTION:\n{question.description}\n\n"
                f"INPUT FORMAT: {question.input_format}\n"
                f"OUTPUT FORMAT: {question.output_format}\n"
                f"CONSTRAINTS:\n" + "\n".join(f"- {c}" for c in question.constraints) + "\n"
            )
        else:
            question_context = f"PROBLEM ID: {request.question_id}\n"

        # Limit inputs for security & sanity
        safe_message = request.message[:2000]
        safe_code = (request.code or "")[:settings.MAX_SOURCE_SIZE_BYTES]
        safe_execution = (request.execution_output or "")[:5000]

        is_solution_request = self._detect_solution_request(safe_message)

        # Context assembly for Gemini
        context_prompt = (
            f"=== ASSIGNED QUESTION CONTEXT ===\n"
            f"{question_context}\n"
            f"=== STUDENT PROGRAMMING ENVIRONMENT ===\n"
            f"Language: {request.language}\n\n"
            f"=== STUDENT'S CURRENT CODE ===\n"
            f"```{request.language}\n{safe_code}\n```\n\n"
        )

        if safe_execution.strip():
            context_prompt += (
                f"=== LATEST EXECUTION RESULT ===\n"
                f"```\n{safe_execution}\n```\n\n"
            )

        if is_solution_request:
            context_prompt += (
                "=== IMPORTANT SECURITY NOTICE ===\n"
                "The student explicitly requested a complete solution or code implementation.\n"
                "Refuse the direct solution request briefly and give a helpful conceptual hint instead.\n\n"
            )

        context_prompt += f"=== STUDENT's CURRENT QUESTION/MESSAGE ===\n{safe_message}"

        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Prepare conversation history if provided
            contents = []
            if request.history:
                for msg in request.history[-6:]:  # include up to last 6 messages
                    role = "user" if msg.role == "user" else "model"
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg.content)]
                        )
                    )

            # Append current prompt
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=context_prompt)]
                )
            )

            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=1024,
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            response_text = response.text or "I am here to guide you! What part of the problem would you like help with?"
            return AIChatResponse(
                response=response_text,
                is_refusal=is_solution_request
            )

        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}", exc_info=True)
            return AIChatResponse(
                response=(
                    "An error occurred while communicating with the AI Tutor. "
                    "Please check your network connection or API configuration."
                ),
                is_refusal=False
            )

ai_service = AIService()
