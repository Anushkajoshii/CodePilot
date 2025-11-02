
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
        html, body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: var(--background);
            color: var(--text);
        }

        :root {
            --background: #f8f8f8;
            --card-bg: #ffffff;
            --text: #222;
            --accent: #b6a268;
            --accent-hover: #9f8c56;
            --border: #ddd;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --background: #0f1115;
                --card-bg: #181a1f;
                --text: #f5f5f5;
                --accent: #c0aa70;
                --accent-hover: #ad965c;
                --border: #2c2c2c;
            }
        }

        .title {
            font-size: 2.8em;
            text-align: center;
            color: var(--accent);
            font-weight: 800;
            margin-bottom: 0.1em;
            letter-spacing: 0.5px;
        }

        .subtitle {
            text-align: center;
            color: var(--text);
            font-size: 1.1em;
            opacity: 0.8;
        }

        .muted {
            text-align: center;
            color: var(--accent);
            font-size: 1rem;
            margin-top: 0.2em;
            margin-bottom: 1rem;
            opacity: 0.9;
        }

        [data-testid="stSidebar"] {
            background-color: var(--card-bg);
            color: var(--text);
            border-right: 1px solid var(--border);
        }

        .stButton>button {
            background-color: var(--accent);
            color: #fff;
            border: none;
            border-radius: 10px;
            height: 3em;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: var(--accent-hover);
            transform: scale(1.03);
        }

        textarea, input, select {
            background-color: var(--card-bg) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 6px !important;
        }

        .stExpander {
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-top: 10px;
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
