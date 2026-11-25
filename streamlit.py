"""CodePilot Streamlit app: three AI agents turn an idea into a working project."""
import os
import shutil
import traceback
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from agent.codegen import RateLimitError, is_rate_limit
from agent.graph import MAX_IMPLEMENTATION_STEPS, build_agent, init_project_root
from agent.preview import preview_html, zip_bytes

APP_DIR = Path(__file__).parent
EXAMPLES_DIR = APP_DIR / "examples"
EXAMPLES = {
    "Tic-tac-toe": {"folder": "tictactoe", "idea": "A two-player tic-tac-toe game"},
    "Sketching app": {"folder": "sketching_app", "idea": "A browser drawing app with a canvas"},
    "Todo app": {"folder": "todo_app", "idea": "A simple to-do list web app"},
}

CSS = """<style>
:root {
    --bg-light: #f6f5f2;
    --bg-dark: #121416;
    --card-light: #ffffff;
    --card-dark: #1b1d22;
    --text-light: #2b2b2b;
    --text-dark: #e6e6e6;
    --accent: #bfa76f;
    --accent-hover: #a6905d;
    --border-light: #d9d9d9;
    --border-dark: #2d2f33;
    --input-light: #f1f1ef;
    --input-dark: #24272c;
}

/* Light / Dark adaptive background */
html, body {
    background-color: var(--bg-light);
    color: var(--text-light);
}

@media (prefers-color-scheme: dark) {
    html, body {
        background-color: var(--bg-dark);
        color: var(--text-dark);
    }
}

/* Title + subtitles */
.title {
    text-align: center;
    font-weight: 800;
    font-size: 3em;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #c8b56b, #bfa76f, #a8915a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.1em;
    text-shadow: 0px 1px 2px rgba(0,0,0,0.15);
}
@media (prefers-color-scheme: dark) {
    .title {
        background: linear-gradient(90deg, #d4c27c, #bfa76f, #a88f55);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
}

.subtitle {
    text-align: center;
    opacity: 0.85;
    font-size: 1.1em;
}
.muted {
    text-align: center;
    color: var(--accent);
    font-size: 1rem;
    margin-bottom: 1.2rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--card-light);
    color: var(--text-light);
    border-right: 1px solid var(--border-light);
}
@media (prefers-color-scheme: dark) {
    [data-testid="stSidebar"] {
        background-color: var(--card-dark);
        color: var(--text-dark);
        border-right: 1px solid var(--border-dark);
    }
}

/* Input + Text Area */
textarea, input, select, .stTextArea textarea {
    background-color: var(--input-light) !important;
    color: var(--text-light) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 10px !important;
    padding: 10px !important;
}
@media (prefers-color-scheme: dark) {
    textarea, input, select, .stTextArea textarea {
        background-color: var(--input-dark) !important;
        color: var(--text-dark) !important;
        border: 1px solid var(--border-dark) !important;
    }
}
textarea:focus, input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 6px rgba(191,167,111,0.35) !important;
}

/* Buttons */
.stButton>button {
    background-color: var(--accent);
    color: #fff;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    height: 3em;
    transition: all 0.25s ease;
}
.stButton>button:hover {
    background-color: var(--accent-hover);
    transform: scale(1.02);
}

/* Expander */
.stExpander {
    background-color: var(--card-light);
    border: 1px solid var(--border-light);
    border-radius: 10px;
}
@media (prefers-color-scheme: dark) {
    .stExpander {
        background-color: var(--card-dark);
        border: 1px solid var(--border-dark);
    }
}
</style>"""


def read_project_files(root: Path) -> dict:
    """Return {relative_path: text} for every text file in a project folder."""
    files = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            try:
                files[str(p.relative_to(root))] = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
    return files


def get_server_key() -> str:
    try:
        return st.secrets.get("GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


def friendly_error(exc: Exception) -> str:
    text = str(exc).lower()
    if isinstance(exc, RateLimitError) or is_rate_limit(exc):
        return ("Groq's free limit is used up for the moment. Wait a minute and try again, "
                "or try a smaller idea. The examples tab works without any key.")
    if "invalid api key" in text or "401" in text or "authentication" in text:
        return "That Groq API key didn't work. Please check it and try again."
    if "no available model" in text:
        return "None of the configured Groq models are available right now. Please try again later."
    return "Something went wrong while generating the project. Please try again with a shorter, clearer idea."


def lang_for(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower()
    return {"js": "javascript", "jsx": "javascript", "ts": "typescript", "py": "python",
            "md": "markdown", "html": "html", "css": "css", "json": "json"}.get(ext, "text")


def show_project(files: dict, download_name: str, key: str) -> None:
    """File list with code on the left, live preview on the right, download below."""
    col_code, col_preview = st.columns(2)
    with col_code:
        st.markdown(f"**Files ({len(files)})**")
        for path, text in files.items():
            with st.expander(path):
                st.code(text, language=lang_for(path))
    with col_preview:
        st.markdown("**Live preview**")
        if "index.html" in files:
            components.html(preview_html(files), height=520, scrolling=True)
        else:
            st.info("No index.html in this project, so there is nothing to preview. Download it to run locally.")
    st.download_button("⬇️ Download project ZIP", data=zip_bytes(files), file_name=download_name,
                       mime="application/zip", use_container_width=True, key=key)


def main():
    st.set_page_config(page_title="CodePilot", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
    st.markdown(CSS, unsafe_allow_html=True)

    st.markdown("<h1 class='title'>🤖 CodePilot</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'><b>Three AI agents that turn an idea into a working web app</b></p>",
                unsafe_allow_html=True)
    st.markdown("<p class='muted'>Planner → Architect → Coder, built with <b>LangGraph</b> and <b>Groq</b></p>",
                unsafe_allow_html=True)

    server_key = get_server_key()

    with st.sidebar:
        st.header("⚙️ Settings")
        user_key = st.text_input("🔑 Your Groq API key", type="password", placeholder="gsk_...")
        if server_key:
            st.caption("Optional. A shared demo key allows one project per visit. "
                       "Get your own free key at console.groq.com for more.")
        else:
            st.caption("Get a free key at console.groq.com. The examples tab needs no key.")
        project_name = st.text_input("🧱 Project name", placeholder="my_app")
        st.markdown("---")
        st.caption(f"Each project has up to {MAX_IMPLEMENTATION_STEPS} files, written one call per file, "
                   "to stay inside Groq's free limits. If Groq asks to slow down, CodePilot waits and retries.")

    tab_examples, tab_generate = st.tabs(["👀 See examples (no key needed)", "🚀 Generate your own"])

    with tab_examples:
        st.markdown("These apps were generated by CodePilot. Pick one, play with the live preview, read the code, "
                    "or download it.")
        choice = st.selectbox("Example", list(EXAMPLES.keys()))
        example = EXAMPLES[choice]
        files = read_project_files(EXAMPLES_DIR / example["folder"])
        st.markdown(f"**Idea given to the agents:** {example['idea']}")
        show_project(files, f"{example['folder']}.zip", key=f"dl_{example['folder']}")

    with tab_generate:
        st.markdown("### ✨ Describe your app")
        user_prompt = st.text_area("🧾 Your idea",
                                   placeholder="e.g. A pomodoro timer with start, pause and reset buttons",
                                   height=120)
        with st.expander("💬 Ideas that work well"):
            st.markdown("- A pomodoro timer with start, pause and reset\n"
                        "- A quiz app with 5 questions and a final score\n"
                        "- A tip calculator that splits the bill between friends")

        if st.button("🚀 Generate app", use_container_width=True):
            api_key = user_key.strip()
            if not user_prompt.strip():
                st.warning("Please describe your app first.")
                st.stop()
            if not api_key:
                if not server_key:
                    st.warning("Please add a Groq API key in the sidebar, or try the examples tab.")
                    st.stop()
                if st.session_state.get("used_demo_key"):
                    st.info("The shared demo key allows one project per visit. "
                            "Add your own free Groq key in the sidebar to keep going.")
                    st.stop()
                st.session_state["used_demo_key"] = True
                api_key = server_key

            project_path = init_project_root(project_name or "project")
            with st.status("Starting the agents...", expanded=True) as status:
                def on_event(kind, detail):
                    status.update(label=detail)
                    st.write(("⏳ " if kind == "waiting" else "✅ ") + detail)

                try:
                    agent = build_agent(api_key, on_event=on_event)
                    agent.invoke({"user_prompt": user_prompt}, {"recursion_limit": 40})
                    status.update(label="Your app is ready 🎉", state="complete", expanded=False)
                    st.session_state["last_project"] = project_path
                except Exception as exc:
                    status.update(label="Generation stopped", state="error")
                    st.error(friendly_error(exc))
                    with st.expander("Technical details"):
                        st.code(traceback.format_exc(limit=3), language="text")
                    shutil.rmtree(project_path, ignore_errors=True)

        last = st.session_state.get("last_project")
        if last and Path(last).exists():
            files = read_project_files(Path(last))
            if files:
                st.success("Here is your app.")
                show_project(files, f"{Path(last).name}.zip", key="dl_generated")

    st.markdown("---")
    st.markdown("<p style='text-align: center; opacity: 0.6;'>Made with ❤️ by <b>Anushka Joshi</b></p>",
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
