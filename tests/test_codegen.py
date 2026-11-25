import pytest

from agent.codegen import (
    RateLimitError, build_context, call_with_fallback, call_with_retry, retry_after_seconds, strip_code_fences,
)


class FakeRateLimit(Exception):
    pass


def test_retry_after_parsing():
    assert retry_after_seconds(Exception("Rate limit reached. Please try again in 12.5s.")) == 12.5
    assert retry_after_seconds(Exception("Please try again in 1m3.5s")) == 63.5
    assert retry_after_seconds(Exception("try again in 450ms")) == 0.45
    assert retry_after_seconds(Exception("no hint"), default=7) == 7


def test_retry_waits_then_succeeds():
    calls, waits = {"n": 0}, []

    def fn():
        calls["n"] += 1
        if calls["n"] < 3:
            raise FakeRateLimit("Error code: 429 - rate_limit_exceeded. Please try again in 2s.")
        return "ok"

    assert call_with_retry(fn, sleep=waits.append) == "ok"
    assert waits == [3.0, 3.0]


def test_retry_gives_up_with_rate_limit_error():
    def fn():
        raise FakeRateLimit("429 Too Many Requests")

    with pytest.raises(RateLimitError):
        call_with_retry(fn, max_attempts=2, sleep=lambda s: None)


def test_non_rate_limit_errors_are_not_retried():
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        raise ValueError("bad input")

    with pytest.raises(ValueError):
        call_with_retry(fn, sleep=lambda s: None)
    assert calls["n"] == 1


def test_fallback_skips_retired_model():
    def make_call(model):
        if model == "old":
            raise Exception("The model `old` has been decommissioned (model_decommissioned)")
        return model

    assert call_with_fallback(["old", "new"], make_call) == "new"


def test_strip_code_fences():
    assert strip_code_fences("```html\n<p>hi</p>\n```") == "<p>hi</p>\n"
    assert strip_code_fences("<p>hi</p>") == "<p>hi</p>\n"


def test_build_context_puts_index_first_and_trims():
    ctx = build_context({"app.js": "x" * 50, "index.html": "<html>"}, max_chars=1000)
    assert ctx.index("index.html") < ctx.index("app.js")
    long = build_context({"index.html": "y" * 5000}, max_chars=1000)
    assert "(trimmed)" in long
