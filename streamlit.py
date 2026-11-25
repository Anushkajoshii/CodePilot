
import streamlit as st
import traceback
import io
import zipfile
import shutil
import tempfile
import os
from pathlib import Path

from agent.graph import build_agent, init_project_root, MAX_IMPLEMENTATION_STEPS


def zip_project_folder(project_path: str):
    """Create a ZIP file of the given project folder and return its path."""
    if not project_path:
        st.error("❌ No project path provided to zip_project_folder()")
        return None

    project_dir = Path(project_path)
    if not project_dir.exists():
        st.warning("⚠️ No project directory found at runtime.")
        return None

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{project_dir.name}.zip")
    shutil.make_archive(zip_path.replace(".zip", ""), "zip", project_dir)
    return zip_path

# ---------------- Examples (no API key needed) ----------------
EXAMPLES_DIR = Path(__file__).parent / "examples"
EXAMPLES = {
    "Todo app": {"folder": "todo_app", "idea": "A simple to-do list web app"},
    "Sketching app": {"folder": "sketching_app", "idea": "A browser drawing app with a canvas"},
    "Tic-tac-toe": {"folder": "tictactoe", "idea": "A two-player tic-tac-toe game"},
}


def read_example_files(folder: str) -> dict:
    """Return {relative_path: text} for every file in an example project."""
    root = EXAMPLES_DIR / folder
    return {
        str(p.relative_to(root)): p.read_text(encoding="utf-8", errors="replace")
        for p in sorted(root.rglob("*")) if p.is_file()
    }


def preview_html(files: dict) -> str:
    """Inline CSS and JS into index.html so the example runs inside the page."""
    html = files.get("index.html", "")
    for path, text in files.items():
        if path.endswith(".css"):
            html = html.replace(f'<link rel="stylesheet" href="{path}">', f"<style>{text}</style>")
        elif path.endswith(".js"):
            html = html.replace(f'<script src="{path}"></script>', f"<script>{text}</script>")
    return html


def zip_bytes(files: dict) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, text in files.items():
            zf.writestr(path, text)
    return buffer.getvalue()


def get_server_key() -> str:
    try:
        return st.secrets.get("GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


def friendly_error(exc: Exception) -> str:
    text = str(exc).lower()
    if "rate limit" in text or "rate_limit" in text or "429" in text or "tokens per" in text:
        return ("The free AI limit has been reached for now. Please try again in a few minutes, "
                "add your own Groq API key in the sidebar, or open the examples tab.")
    if "invalid api key" in text or "401" in text or "authentication" in text:
        return "That Groq API key didn't work. Please check it and try again."
    if "recursion" in text:
        return "The agent needed more steps than allowed. Try a smaller idea or raise the step limit."
    return "Something went wrong while generating the project. Please try again with a shorter, clearer idea."


def main():
    # ---------------- Page Setup ----------------
    st.set_page_config(
        page_title="CodePilot 🚀",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # ---------------- Custom Styling ----------------
    st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)



    # ---------------- Header ----------------
    st.markdown("<h1 class='title'>🤖 CodePilot</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'><b>Three AI agents that turn an idea into a working project</b></p>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Planner → Architect → Coder, built with <b>LangGraph</b> and <b>Groq</b></p>", unsafe_allow_html=True)
    st.write("")

    server_key = get_server_key()

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.header("⚙️ Settings")
        user_key = st.text_input("🔑 Your Groq API key (optional)", type="password", placeholder="gsk_...")
        if server_key:
            st.caption("Optional: a shared demo key is available, limited to one project per visit. Add your own free key from console.groq.com for more.")
        else:
            st.caption("Get a free key at console.groq.com. Or try the examples tab, which needs no key.")
        recursion_limit = st.number_input(
            "🔁 Step limit", min_value=10, max_value=150, value=60,
            help="The most steps the agents may take. Lower is faster and uses fewer tokens.",
        )
        project_name = st.text_input("🧱 Project name", placeholder="my_app")
        st.markdown("---")
        st.caption(f"Projects are capped at {MAX_IMPLEMENTATION_STEPS} files to keep runs fast and within free limits.")

    tab_examples, tab_generate = st.tabs(["👀 See examples (no key needed)", "🚀 Generate your own"])

    # ---------------- Examples ----------------
    with tab_examples:
        st.markdown("These projects were generated by CodePilot. Pick one to see the code, run it, and download it.")
        choice = st.selectbox("Example", list(EXAMPLES.keys()))
        example = EXAMPLES[choice]
        files = read_example_files(example["folder"])
        st.markdown(f"**Idea given to the agents:** {example['idea']}")
        col_code, col_preview = st.columns(2)
        with col_code:
            st.markdown(f"**Files created ({len(files)})**")
            for path, text in files.items():
                with st.expander(path):
                    lang = path.rsplit(".", 1)[-1].replace("jsx", "javascript").replace("js", "javascript").replace("md", "markdown")
                    st.code(text, language=lang)
        with col_preview:
            st.markdown("**Live preview**")
            if "index.html" in files:
                st.components.v1.html(preview_html(files), height=480, scrolling=True)
        st.download_button(
            "⬇️ Download this example", data=zip_bytes(files),
            file_name=f"{example['folder']}.zip", mime="application/zip", use_container_width=True,
        )

    # ---------------- Generate ----------------
    with tab_generate:
        st.markdown("### ✨ Describe your project")
        user_prompt = st.text_area(
            "🧾 Project description",
            placeholder="e.g. A pomodoro timer web app with start, pause and reset buttons",
            height=130,
        )
        with st.expander("💬 Example ideas"):
            st.markdown(
                "- A to-do list web app with local storage\n"
                "- A simple calculator in HTML, CSS and JavaScript\n"
                "- A quiz app with 5 questions and a score at the end"
            )

        if st.button("🚀 Generate project", use_container_width=True):
            api_key = user_key.strip()
            if not user_prompt.strip():
                st.warning("Please describe your project first.")
                st.stop()
            if not api_key:
                if not server_key:
                    st.warning("Please add a Groq API key in the sidebar, or try the examples tab.")
                    st.stop()
                if st.session_state.get("used_demo_key"):
                    st.info("The shared demo key allows one project per visit. Add your own free Groq key in the sidebar to keep going.")
                    st.stop()
                st.session_state["used_demo_key"] = True
                api_key = server_key

            try:
                project_path = init_project_root(project_name or "project")
                agent = build_agent(api_key)
                with st.spinner("🪄 The agents are planning and writing your project. This can take a minute or two..."):
                    result = agent.invoke({"user_prompt": user_prompt}, {"recursion_limit": int(recursion_limit)})

                zip_path = zip_project_folder(project_path)
                if zip_path and os.path.exists(zip_path):
                    st.success("🎉 Your project is ready.")
                    with open(zip_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download project ZIP", data=f,
                            file_name=f"{Path(project_path).name}.zip",
                            mime="application/zip", use_container_width=True,
                        )
                    with st.expander("📋 Agent output (plan and tasks)"):
                        st.json(result, expanded=False)
                else:
                    st.warning("The agents finished but no files were written. Try a clearer, smaller idea.")
            except Exception as exc:
                st.error(friendly_error(exc))
                with st.expander("Technical details"):
                    st.code(traceback.format_exc(limit=3), language="text")

    # ---------------- Footer ----------------
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: var(--text); opacity: 0.6;'>Made with ❤️ by <b>Anushka Joshi</b></p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
