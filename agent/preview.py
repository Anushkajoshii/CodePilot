"""Turn a multi-file HTML/CSS/JS project into one self-contained page for a live preview."""
import io
import re
import zipfile

_LINK = re.compile(r"<link\b[^>]*\bhref=[\"']([^\"']+\.css)[\"'][^>]*>", re.IGNORECASE)
_SCRIPT = re.compile(r"<script\b[^>]*\bsrc=[\"']([^\"']+\.js)[\"'][^>]*>\s*</script>", re.IGNORECASE)


def _norm(path: str) -> str:
    return path.lstrip("./")


def preview_html(files: dict[str, str]) -> str:
    """Inline local CSS into <head> and local JS at the end of <body>.

    Scripts are moved to the end of the body so code that expects the page to be
    loaded (including `defer` scripts in <head>) works the same as in a browser.
    Remote links (CDNs) are left untouched.
    """
    html = files.get("index.html", "")
    local = {_norm(p): text for p, text in files.items()}

    styles: list[str] = []
    scripts: list[str] = []

    def take_css(m: re.Match) -> str:
        path = _norm(m.group(1))
        if path in local:
            styles.append(local[path])
            return ""
        return m.group(0)

    def take_js(m: re.Match) -> str:
        path = _norm(m.group(1))
        if path in local:
            scripts.append(local[path])
            return ""
        return m.group(0)

    html = _LINK.sub(take_css, html)
    html = _SCRIPT.sub(take_js, html)

    style_block = "".join(f"<style>\n{css}\n</style>\n" for css in styles)
    # Escape any closing script tag inside inlined code so it cannot end the block early.
    script_block = "".join(
        "<script>\n" + js.replace("</script", "<\\/script") + "\n</script>\n" for js in scripts
    )

    if re.search(r"</head>", html, re.IGNORECASE):
        html = re.sub(r"</head>", style_block + "</head>", html, count=1, flags=re.IGNORECASE)
    else:
        html = style_block + html

    if re.search(r"</body>", html, re.IGNORECASE):
        # Inline scripts at the end of <body> run after the page markup exists,
        # and before DOMContentLoaded fires, so both coding styles work.
        html = re.sub(r"</body>", script_block + "</body>", html, count=1, flags=re.IGNORECASE)
    else:
        html = html + script_block
    return html


def zip_bytes(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, text in files.items():
            zf.writestr(path, text)
    return buffer.getvalue()
