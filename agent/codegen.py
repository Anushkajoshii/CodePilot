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


class BadOutputError(RuntimeError):
    """Raised when a model keeps answering in the wrong format (e.g. prose instead of JSON)."""


def is_bad_output(exc: Exception) -> bool:
    """The model answered, but not in the structured format we asked for."""
    if isinstance(exc, BadOutputError):
        return True
    name = type(exc).__name__
    text = str(exc).lower()
    return name in {"ValidationError", "OutputParserException", "JSONDecodeError"} or any(
        k in text for k in (
            "tool_use_failed", "did not call a tool", "failed_generation",
            "json_validate_failed", "failed to parse", "validation error", "invalid json",
        )
    )


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
    """Try each model in order, moving on if a model is retired, unavailable, or keeps giving bad output."""
    last_exc: Exception | None = None
    for model in models:
        try:
            return make_call(model)
        except Exception as exc:  # noqa: BLE001
            if is_model_unavailable(exc) or isinstance(exc, BadOutputError):
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


# ---------------------------------------------------------------------------
# Making generated apps run when index.html is opened directly in a browser
# ---------------------------------------------------------------------------

_EXPORT_LIST = re.compile(r"^\s*export\s*\{[^}]*\}\s*(?:from\s*['\"][^'\"]+['\"])?\s*;?\s*$", re.MULTILINE)
_EXPORT_DEFAULT_NAMED = re.compile(r"^(\s*)export\s+default\s+(?=(?:async\s+)?(?:function|class)\b)", re.MULTILINE)
_EXPORT_DEFAULT_EXPR = re.compile(r"^\s*export\s+default\s+[\w$.]+\s*;?\s*$", re.MULTILINE)
_EXPORT_DECL = re.compile(r"^(\s*)export\s+(?=(?:async\s+)?(?:function|class|const|let|var)\b)", re.MULTILINE)
_IMPORT = re.compile(r"^\s*import\s+(?:[\s\S]*?\s+from\s+)?['\"][^'\"]+['\"]\s*;?\s*$", re.MULTILINE)
_MODULE_ATTR = re.compile(r"\s+type=[\"']module[\"']", re.IGNORECASE)


def make_browser_safe_js(code: str) -> tuple[str, bool]:
    """Remove ES module syntax so files work as plain <script> tags sharing globals."""
    new = _EXPORT_LIST.sub("", code)
    new = _EXPORT_DEFAULT_NAMED.sub(r"\1", new)
    new = _EXPORT_DEFAULT_EXPR.sub("", new)
    new = _EXPORT_DECL.sub(r"\1", new)
    new = _IMPORT.sub("", new)
    return new, new != code


def make_browser_safe_html(html: str) -> tuple[str, bool]:
    """Load scripts as classic scripts (no type="module"), matching make_browser_safe_js."""
    new = _MODULE_ATTR.sub("", html)
    return new, new != html


_LOCAL_REF = re.compile(r"""(?:src|href)=["']([^"'#?:]+?\.(?:js|css|png|jpe?g|gif|svg|webp|ico|mp3|wav|json))["']""", re.I)
_CSS_URL = re.compile(r"""url\(\s*["']?([^"')#?:]+?\.(?:png|jpe?g|gif|svg|webp|woff2?|ttf))["']?\s*\)""", re.I)


def find_missing_files(files: dict[str, str]) -> list[str]:
    """List local files that HTML or CSS refers to but the project does not contain."""
    have = {p.lstrip("./") for p in files}
    missing = []
    for path, text in files.items():
        refs = _LOCAL_REF.findall(text) if path.endswith(".html") else []
        refs += _CSS_URL.findall(text) if path.endswith((".css", ".html")) else []
        for ref in refs:
            ref = ref.lstrip("./")
            if ref not in have and ref not in missing:
                missing.append(ref)
    return missing


def unbalanced_brackets(code: str) -> bool:
    """Rough JS sanity check: are (), [], {} balanced outside strings and comments?

    Catches files that were cut off mid-way. Regex literals are not parsed, so this is a
    warning signal only, never used to block a project.
    """
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    i, n = 0, len(code)
    while i < n:
        ch = code[i]
        nxt = code[i + 1] if i + 1 < n else ""
        if ch == "/" and nxt == "/":
            j = code.find("\n", i)
            i = n if j == -1 else j
            continue
        if ch == "/" and nxt == "*":
            j = code.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue
        if ch in "'\"`":
            quote, i = ch, i + 1
            while i < n and code[i] != quote:
                i += 2 if code[i] == "\\" else 1
            if i >= n:
                return True  # string never closed
            i += 1
            continue
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return True
        i += 1
    return bool(stack)
