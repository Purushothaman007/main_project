import sys
from types import ModuleType, SimpleNamespace

from app.core.config import settings
from app.services import hint_service
from app.schemas.hint import HintRequest


def test_genai_client_uses_configured_api_key(monkeypatch):
    expected_client = object()
    fake_genai = SimpleNamespace(
        Client=lambda *, api_key: expected_client if api_key == "configured-key" else None
    )
    fake_google = SimpleNamespace(genai=fake_genai)

    monkeypatch.setattr(settings, "GEMINI_API_KEY", " configured-key ")
    monkeypatch.setattr(hint_service, "_genai_client", None)
    monkeypatch.setitem(sys.modules, "google", fake_google)

    assert hint_service._get_genai_client() is expected_client


def test_generate_hint_uses_configured_model(monkeypatch):
    requested_models = []
    fake_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: (
                requested_models.append(kwargs["model"])
                or SimpleNamespace(text="Consider what state you need to track.")
            )
        )
    )
    fake_google = ModuleType("google")
    fake_genai = ModuleType("google.genai")
    fake_types = ModuleType("google.genai.types")
    fake_types.GenerateContentConfig = lambda **kwargs: kwargs
    fake_genai.types = fake_types
    fake_google.genai = fake_genai

    monkeypatch.setattr(settings, "GEMINI_MODEL", "configured-model")
    monkeypatch.setattr(hint_service, "_get_genai_client", lambda: fake_client)
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_types)

    response = hint_service.generate_hint(
        HintRequest(language="python", student_message="How should I start?"),
        client_key="test-client",
    )

    assert requested_models == ["configured-model"]
    assert response.message == "Consider what state you need to track."


def test_generate_hint_returns_fallback_for_missing_model(monkeypatch, caplog):
    class ModelNotFoundError(Exception):
        code = 404

    def generate_content(**kwargs):
        raise ModelNotFoundError(
            '404 NOT_FOUND: "This model models/gemini-3.8-flash is no longer available."'
        )

    fake_client = SimpleNamespace(
        models=SimpleNamespace(generate_content=generate_content)
    )
    fake_google = ModuleType("google")
    fake_genai = ModuleType("google.genai")
    fake_types = ModuleType("google.genai.types")
    fake_types.GenerateContentConfig = lambda **kwargs: kwargs
    fake_genai.types = fake_types
    fake_google.genai = fake_genai

    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")
    monkeypatch.setattr(hint_service, "_get_genai_client", lambda: fake_client)
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_types)

    response = hint_service.generate_hint(
        HintRequest(language="python", student_message="How should I start?"),
        client_key="missing-model-test",
    )

    assert response.message == hint_service._FALLBACK_HINTS[1]
    assert "model=gemini-3.8-flash" in caplog.text
    assert "404 NOT_FOUND" not in response.message


def test_generate_hint_uses_groq_when_gemini_is_unavailable(monkeypatch):
    class ServiceUnavailableError(Exception):
        code = 503

    gemini_attempts = []

    def generate_content(**kwargs):
        gemini_attempts.append(kwargs["model"])
        raise ServiceUnavailableError("503 UNAVAILABLE: temporary outage")

    groq_calls = []
    fake_groq_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: (
                    groq_calls.append(kwargs)
                    or SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(
                                    content="What information must your program remember?"
                                )
                            )
                        ]
                    )
                )
            )
        )
    )
    fake_groq_module = ModuleType("groq")
    fake_groq_module.Groq = lambda *, api_key: fake_groq_client
    fake_google = ModuleType("google")
    fake_genai = ModuleType("google.genai")
    fake_types = ModuleType("google.genai.types")
    fake_types.GenerateContentConfig = lambda **kwargs: kwargs
    fake_genai.types = fake_types
    fake_google.genai = fake_genai

    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test-groq-key")
    monkeypatch.setattr(settings, "GROQ_MODEL", "test-groq-model")
    monkeypatch.setattr(hint_service, "_get_genai_client", lambda: SimpleNamespace(
        models=SimpleNamespace(generate_content=generate_content)
    ))
    monkeypatch.setattr(hint_service, "_groq_client", None)
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", fake_types)
    monkeypatch.setitem(sys.modules, "groq", fake_groq_module)

    response = hint_service.generate_hint(
        HintRequest(language="python", student_message="How should I start?"),
        client_key="groq-fallback-test",
    )

    assert gemini_attempts == ["gemini-3.8-flash", "gemini-3.8-flash"]
    assert len(groq_calls) == 1
    assert groq_calls[0]["model"] == "test-groq-model"
    assert response.message == "What information must your program remember?"


def test_selecting_groq_uses_it_before_gemini(monkeypatch):
    groq_requests = []

    def generate_groq(req, user_prompt, history, hint_type):
        groq_requests.append(req.provider)
        return hint_service.HintResponse(
            hint_level=req.hint_level,
            hint_type=hint_type,
            message="What value should be tracked as you process each item?",
            next_hint_available=True,
        )

    def unexpected_gemini_call():
        raise AssertionError("Gemini should not run when Groq is selected and available")

    monkeypatch.setattr(hint_service, "_generate_groq_hint", generate_groq)
    monkeypatch.setattr(hint_service, "_get_genai_client", unexpected_gemini_call)

    response = hint_service.generate_hint(
        HintRequest(
            provider="groq",
            language="python",
            student_message="How should I start?",
        ),
        client_key="selected-groq-test",
    )

    assert groq_requests == ["groq"]
    assert response.message == "What value should be tracked as you process each item?"


