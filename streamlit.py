
import streamlit as st
import traceback
import shutil
import tempfile
import os
from pathlib import Path

from agent.graph import build_agent, init_project_root


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


# def main():
#     st.set_page_config(page_title="CodePilot", page_icon="🤖", layout="wide")

#     st.title("🤖 CodePilot – Your AI Co-Pilot for App Generation")
#     st.write("Generate AI or web projects using LangGraph + Groq.")

#     with st.sidebar:
#         st.header("⚙️ Settings")
#         api_key = st.text_input("🔑 Groq API Key", type="password", placeholder="gsk_...")
#         recursion_limit = st.number_input("Recursion Limit", min_value=10, max_value=1000, value=100)
#         project_name = st.text_input("🧱 Project Name", placeholder="my_ai_app")

#     user_prompt = st.text_area(
#         "🧾 Project Description",
#         placeholder="e.g. Build a web-based calculator using Flask",
#         height=150,
#     )

#     if st.button("🚀 Generate Project", use_container_width=True):
#         if not user_prompt.strip():
#             st.warning("Please enter a project description.")
#             st.stop()
#         if not api_key.strip():
#             st.warning("Please enter your Groq API key.")
#             st.stop()

#         try:
#             st.info("🧱 Initializing project...")
#             project_path = init_project_root(project_name or "project")
#             if not project_path:
#                 st.error("❌ Failed to initialize project folder.")
#                 st.stop()

#             st.info("🤖 Running agent... This may take a few minutes ⏳")
#             agent = build_agent(api_key)

#             with st.spinner("Generating your project..."):
#                 result = agent.invoke(
#                     {"user_prompt": user_prompt},
#                     {"recursion_limit": recursion_limit},
#                 )

#             st.success("✅ Project generation completed successfully!")
#             st.subheader("📋 Final State:")
#             st.json(result)

#             st.info("📦 Packaging your project files...")
#             zip_path = zip_project_folder(project_path)

#             if zip_path and os.path.exists(zip_path):
#                 with open(zip_path, "rb") as f:
#                     st.download_button(
#                         "⬇️ Download Project ZIP",
#                         data=f,
#                         file_name=f"{Path(project_path).name}.zip",
#                         mime="application/zip",
#                         use_container_width=True,
#                     )
#                 st.success("🎉 Your project is ready to download!")
#             else:
#                 st.warning("⚠️ No project files found to package.")

#         except Exception as e:
#             st.error("❌ An unexpected error occurred.")
#             st.text("Detailed Traceback:")
#             st.code(traceback.format_exc(), language="python")
#     # Footer
#     st.divider()
#     st.markdown(
#         "<p style='text-align: center;'>Made by <b>Anushka Joshi</b>.</p>", 
#         unsafe_allow_html=True
#     )


# if __name__ == "__main__":
#     main()


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
    st.markdown("<p class='subtitle'><b>Your AI copilot for app generation</b></p>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Generate AI or web projects using <b>LangGraph + Groq</b></p>", unsafe_allow_html=True)
    st.write("")

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.header("⚙️ Settings")

        api_key = st.text_input("🔑 Groq API Key", type="password", placeholder="gsk_...")
        st.caption("Your Groq API key is required to use the Groq model for app generation.")

        recursion_limit = st.number_input(
            "🔁 Recursion Limit",
            min_value=10, max_value=1000, value=100,
            help=(
                "Defines how deep the AI can recursively generate or refine project components.\n\n"
                "- Lower = Faster, simpler generations.\n"
                "- Higher = More complex, detailed outputs (but slower)."
            )
        )

        project_name = st.text_input("🧱 Project Name", placeholder="my_ai_app")
        st.caption("This will be used to create a folder for your generated project.")

        st.markdown("---")
        st.caption("💡 Tip: Use a clear, detailed prompt for best results.")

    # ---------------- Main Input ----------------
    st.markdown("### ✨ Describe Your Project")
    user_prompt = st.text_area(
        "🧾 Project Description",
        placeholder="e.g. Build a web-based calculator using Flask and deploy it to Streamlit Cloud.",
        height=150,
    )

    # 🧩 Example Prompts Section
    with st.expander("💬 Example Prompts (click to view)", expanded=False):
        st.markdown("""
        - Create a to-do list web app using React and FastAPI  
        - Build a simple calculator using JavaScript  
        - Develop a simple blogging app with Flask and SQLite
        """)

    # ---------------- Generate Button ----------------
    if st.button("🚀 Generate Project", use_container_width=True):
        if not user_prompt.strip():
            st.warning("Please enter a project description.")
            st.stop()
        if not api_key.strip():
            st.warning("Please enter your Groq API key.")
            st.stop()

        try:
            st.info("🧱 Initializing project...")
            project_path = init_project_root(project_name or "project")

            if not project_path:
                st.error("❌ Failed to initialize project folder.")
                st.stop()

            st.info("🤖 Running agent... This may take a few minutes ⏳")
            agent = build_agent(api_key)

            with st.spinner("🪄 Generating your project..."):
                result = agent.invoke(
                    {"user_prompt": user_prompt},
                    {"recursion_limit": recursion_limit},
                )

            st.success("🎉 Project generation completed successfully!")
            with st.expander("📋 View Final Agent Output", expanded=False):
                st.json(result)

            st.info("📦 Packaging your project files...")
            zip_path = zip_project_folder(project_path)

            if zip_path and os.path.exists(zip_path):
                with open(zip_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Project ZIP",
                        data=f,
                        file_name=f"{Path(project_path).name}.zip",
                        mime="application/zip",
                        use_container_width=True,
                    )
                st.balloons()
                st.success("🎊 Your project is ready to download!")
            else:
                st.warning("⚠️ No project files found to package.")

        except Exception as e:
            st.error("❌ Oops, something went wrong.")
            st.code(traceback.format_exc(), language="python")

    # ---------------- Footer ----------------
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: var(--text); opacity: 0.6;'>Made with ❤️ by <b>Anushka Joshi</b></p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
