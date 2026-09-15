from app.api import MessageIn, ArtifactIn
from pydantic import ValidationError
import pytest


def test_message_request_defaults_to_ollama():
    payload = MessageIn(content="What does Lenny say about growth?")
    assert payload.provider == "ollama"


def test_message_request_accepts_anthropic():
    payload = MessageIn(
        content="What does Lenny say about growth?",
        provider="anthropic",
    )
    assert payload.provider == "anthropic"


def test_message_request_rejects_invalid_provider():
    with pytest.raises(ValidationError):
        MessageIn(
            content="Test question",
            provider="invalid",
        )


def test_artifact_request_accepts_html():
    payload = ArtifactIn(
        request="Create a landing page",
        type="html",
        provider="ollama",
    )
    assert payload.type == "html"
    assert payload.provider == "ollama"


def test_artifact_request_rejects_invalid_type():
    with pytest.raises(ValidationError):
        ArtifactIn(
            request="Create something",
            type="pdf",
            provider="ollama",
        )