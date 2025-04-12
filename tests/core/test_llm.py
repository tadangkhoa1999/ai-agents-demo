import os
from unittest.mock import patch

import pytest
from langchain_community.chat_models import FakeListChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from core.llm import get_model
from schema.models import (
    FakeModelName,
    OllamaModelName,
    OpenAIModelName,
)


def test_get_model_openai():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        model = get_model(OpenAIModelName.GPT_4O_MINI)
        assert isinstance(model, ChatOpenAI)
        assert model.model_name == "gpt-4o-mini"
        assert model.temperature == 0.5
        assert model.streaming is True


def test_get_model_ollama():
    with patch("core.settings.settings.OLLAMA_MODEL", "llama3.3"):
        model = get_model(OllamaModelName.OLLAMA_GENERIC)
        assert isinstance(model, ChatOllama)
        assert model.model == "llama3.3"
        assert model.temperature == 0.5


def test_get_model_fake():
    model = get_model(FakeModelName.FAKE)
    assert isinstance(model, FakeListChatModel)
    assert model.responses == ["This is a test response from the fake model."]


def test_get_model_invalid():
    with pytest.raises(ValueError, match="Unsupported model:"):
        # Using type: ignore since we're intentionally testing invalid input
        get_model("invalid_model")  # type: ignore
