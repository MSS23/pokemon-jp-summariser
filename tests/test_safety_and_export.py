"""Offline checks for the SSRF guard, Showdown export, API-error handling and model config."""

import pytest
from types import SimpleNamespace

from core.analyzer import GeminiVGCAnalyzer
from utils.config import Config
from utils.errors import APILimitError
from utils.utils import assert_public_url, block_private_redirects, create_pokepaste


@pytest.mark.parametrize("url", [
    "file:///etc/passwd",
    "ftp://note.com/x",
    "http://127.0.0.1:8501/",
    "http://169.254.169.254/latest/meta-data/",
    "http://10.0.0.5/",
    "http://[::1]/",
    "http://localhost/",
])
def test_ssrf_guard_rejects_non_public_urls(url):
    with pytest.raises(ValueError):
        assert_public_url(url)


def test_ssrf_guard_allows_public_ip():
    assert_public_url("https://8.8.8.8/")  # IP literal: no DNS needed


def test_redirect_hook_blocks_private_target():
    redirect = SimpleNamespace(is_redirect=True, url="https://note.com/a",
                               headers={"location": "http://169.254.169.254/"})
    with pytest.raises(ValueError):
        block_private_redirects(redirect)
    block_private_redirects(SimpleNamespace(is_redirect=False))  # normal responses pass


def test_pokepaste_is_showdown_importable():
    paste = create_pokepaste([
        {"name": "Incineroar", "held_item": "Not specified", "ability": "Intimidate",
         "tera_type": "Not specified", "nature": "Not specified",
         "evs": "252/0/4/0/252/0", "moves": ["Fake Out", "Not specified"]},
        {"name": "Flutter Mane", "evs": "Not specified", "nature": "Timid",
         "ev_spread": {"HP": 4, "Special Attack": 252, "Speed": 252, "total": 508}},
    ])
    assert "Not specified" not in paste
    assert "Incineroar\nAbility: Intimidate\nEVs: 252 HP / 4 Def / 252 SpD\n- Fake Out" in paste
    assert "EVs: 4 HP / 252 SpA / 252 Spe\nTimid Nature" in paste


def test_api_errors_are_not_retried():
    analyzer = GeminiVGCAnalyzer.__new__(GeminiVGCAnalyzer)
    calls = []

    def quota_error(prompt, content):
        calls.append("standard")
        raise APILimitError("quota", error_type="quota_exceeded")

    analyzer._generate_standard = quota_error
    analyzer._generate_with_reduced_content = lambda *a: calls.append("reduced")
    analyzer._generate_with_simplified_prompt = lambda *a: calls.append("simplified")
    with pytest.raises(APILimitError):
        analyzer._generate_with_fallbacks("prompt", "content")
    assert calls == ["standard"]


def test_gemini_model_env_override(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    assert Config.get_gemini_model() == Config.DEFAULT_GEMINI_MODEL
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")
    assert Config.get_gemini_model() == "gemini-test-model"
