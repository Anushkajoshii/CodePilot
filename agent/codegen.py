"""Helpers for calling the LLM within Groq free-tier limits.

- `call_with_retry` waits and retries when Groq says "rate limit, try again in Xs".
- `call_with_fallback` moves to the next model if one is retired or unavailable.
- `build_context` gives the coder only a trimmed view of files already written,
  so each call stays small.
"""
import logging
import re
import time
from typing import Callable, Sequence, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


class RateLimitError(RuntimeError):
    """Raised when the provider keeps rate-limiting after all retries."""


def is_rate_limit(exc: Exception) -> bool:
    text = str(exc).lower()
    return "rate limit" in text or "rate_limit" in text or "429" in text or "too many requests" in text


def is_model_unavailable(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(k in text for k in ("model_decommissioned", "model_not_found", "does not exist", "decommissioned"))


def retry_after_seconds(exc: Exception, default: float = 10.0) -> float:
    """Read 'try again in 12.5s' / 'in 1m3s' from a rate-limit message."""
    text = str(exc)
    m = re.search(r"try again in (?:(\d+)m)?([\d.]+)s", text)
    if m:
        minutes = float(m.group(1) or 0)
        return minutes * 60 + float(m.group(2))
    m = re.search(r"try again in (\d+)ms", text)
    if m:
        return float(m.group(1)) / 1000
    return default


def call_with_retry(
    fn: Callable[[], T],
    max_attempts: int = 4,
    max_wait: float = 45.0,
    sleep: Callable[[float], None] = time.sleep,
    on_wait: Callable[[float], None] | None = None,
) -> T:
    """Run fn(); on a rate limit, wait as long as the provider asks (capped) and retry."""
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - provider SDKs raise many types
            if not is_rate_limit(exc):
                raise
            if attempt == max_attempts:
                raise RateLimitError(str(exc)) from exc
            wait = min(retry_after_seconds(exc) + 1.0, max_wait)
            logger.info("Rate limited, waiting %.1fs (attempt %d/%d)", wait, attempt, max_attempts)
            if on_wait:
                on_wait(wait)
            sleep(wait)
    raise RuntimeError("unreachable")


def call_with_fallback(models: Sequence[str], make_call: Callable[[str], T]) -> T:
    """Try each model in order, moving on only if a model is retired or unavailable."""
    last_exc: Exception | None = None
    for model in models:
        try:
            return make_call(model)
        except Exception as exc:  # noqa: BLE001
            if is_model_unavailable(exc):
                logger.warning("Model %s unavailable, trying next: %s", model, exc)
                last_exc = exc
                continue
            raise
    raise RuntimeError(f"No available model among {list(models)}") from last_exc


_FENCE = re.compile(r"^\s*```[\w+-]*\s*\n(.*?)\n?```\s*$", re.DOTALL)


def strip_code_fences(text: str) -> str:
    """Remove a single wrapping ``` fence if the model added one anyway."""
    text = (text or "").strip("\n")
    m = _FENCE.match(text)
    return (m.group(1) if m else text).strip("\n") + "\n"


def build_context(written: dict[str, str], max_chars: int = 6000) -> str:
    """Show earlier files to the coder, index.html first, trimmed to a character budget."""
    order = sorted(written, key=lambda p: (p != "index.html", p))
    parts, used = [], 0
    for path in order:
        content = written[path]
        room = max_chars - used
        if room <= 200:
            parts.append(f"--- {path} (omitted to save tokens)")
            continue
        snippet = content if len(content) <= room else content[:room] + "\n... (trimmed)"
        parts.append(f"--- {path}\n{snippet}")
        used += len(snippet)
    return "\n".join(parts)
