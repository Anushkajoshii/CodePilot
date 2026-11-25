from pathlib import Path

from agent.preview import preview_html

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def load(folder):
    root = EXAMPLES / folder
    return {str(p.relative_to(root)): p.read_text(encoding="utf-8") for p in root.rglob("*") if p.is_file()}


def test_inlines_deferred_head_script_and_css():
    files = {
        "index.html": '<html><head><link rel="stylesheet" href="style.css">'
                      '<script defer src="script.js"></script></head><body><div id="a"></div></body></html>',
        "style.css": "body{color:red}",
        "script.js": "document.getElementById('a').textContent='hi';",
    }
    html = preview_html(files)
    assert "body{color:red}" in html
    assert "getElementById('a')" in html
    assert 'src="script.js"' not in html
    # script must come after the element it touches
    assert html.index('id="a"') < html.index("getElementById('a')")


def test_leaves_remote_links_alone():
    files = {"index.html": '<head><script src="https://cdn.example.com/x.js"></script></head><body></body>'}
    assert "https://cdn.example.com/x.js" in preview_html(files)


def test_closing_script_tag_inside_js_is_escaped():
    files = {"index.html": "<body><script src='a.js'></script></body>", "a.js": "var s='</script>';"}
    html = preview_html(files)
    assert html.count("</script>") == 1


def test_every_example_inlines_all_local_files():
    for folder in ("tictactoe", "sketching_app", "todo_app"):
        files = load(folder)
        html = preview_html(files)
        for path, text in files.items():
            if path.endswith((".js", ".css")) and "src/" not in path:
                assert text.strip()[:40] in html, f"{folder}/{path} not inlined"
