# # import streamlit as st
# # import argparse
# # import sys
# # import traceback

# # from agent.graph import agent
# # def main():
# #     st.set_page_config(page_title="Engineering Project Planner", page_icon="🧠", layout="wide")

# #     st.title("🧠 Engineering Project Planner")
# #     st.write("Generate and plan your AI or engineering project using the agentic workflow.")

# #     with st.sidebar:
# #         st.header("⚙️ Settings")
# #         recursion_limit = st.number_input(
# #             "Recursion Limit",
# #             min_value=10,
# #             max_value=1000,
# #             value=100,
# #             step=10,
# #             help="Limit for recursion depth during processing."
# #         )

# #     user_prompt = st.text_area(
# #         "🧾 Enter your project prompt",
# #         placeholder="e.g. Build a web-based calculator app using Flask",
# #         height=150
# #     )

# #     if st.button("🚀 Run Agent", use_container_width=True):
# #         if not user_prompt.strip():
# #             st.warning("Please enter a project prompt first.")
# #             st.stop()

# #         st.info("Running agent... Please wait ⏳")
# #         try:
# #             with st.spinner("Processing your request..."):
# #                 result = agent.invoke(
# #                     {"user_prompt": user_prompt},
# #                     {"recursion_limit": recursion_limit}
# #                 )

# #             st.success("✅ Agent completed successfully!")
# #             st.subheader("Final State:")
# #             st.json(result)

# #         except Exception as e:
# #             st.error("❌ An error occurred while running the agent.")
# #             st.exception(e)
# #             st.text("Detailed Traceback:")
# #             st.code(traceback.format_exc(), language="python")

# # if __name__ == "__main__":
# #     main()


# import streamlit as st
# import argparse
# import sys
# import traceback
# import shutil
# import io
# import zipfile
# import os
# from pathlib import Path

# from agent.graph import agent

# # Path where your project files are generated
# PROJECT_ROOT = Path.cwd() / "generated_project"


# def zip_project_folder(folder_path: Path) -> bytes:
#     """Create a ZIP archive of the generated project folder."""
#     zip_buffer = io.BytesIO()
#     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
#         for root, _, files in os.walk(folder_path):
#             for file in files:
#                 file_path = Path(root) / file
#                 zipf.write(file_path, arcname=file_path.relative_to(folder_path))
#     zip_buffer.seek(0)
#     return zip_buffer.getvalue()


# def main():
#     st.set_page_config(page_title="Engineering Project Planner", page_icon="🧠", layout="wide")

#     st.title("🧠 Engineering Project Planner")
#     st.write("Generate and plan your AI or engineering project using the agentic workflow.")

#     with st.sidebar:
#         st.header("⚙️ Settings")
#         recursion_limit = st.number_input(
#             "Recursion Limit",
#             min_value=10,
#             max_value=1000,
#             value=100,
#             step=10,
#             help="Limit for recursion depth during processing."
#         )

#     user_prompt = st.text_area(
#         "🧾 Enter your project prompt",
#         placeholder="e.g. Build a web-based calculator app using Flask",
#         height=150
#     )

#     if st.button("🚀 Run Agent", use_container_width=True):
#         if not user_prompt.strip():
#             st.warning("Please enter a project prompt first.")
#             st.stop()

#         st.info("Running agent... Please wait ⏳")
#         try:
#             with st.spinner("Processing your request..."):
#                 result = agent.invoke(
#                     {"user_prompt": user_prompt},
#                     {"recursion_limit": recursion_limit}
#                 )

#             st.success("✅ Agent completed successfully!")
#             st.subheader("Final State:")
#             st.json(result)

#             # --- Download project section ---
#             if PROJECT_ROOT.exists():
#                 st.subheader("📂 Generated Project Files")
#                 for f in PROJECT_ROOT.rglob("*"):
#                     if f.is_file():
#                         st.write(f"- {f.relative_to(PROJECT_ROOT)}")

#                 # Create ZIP and provide download button
#                 zip_bytes = zip_project_folder(PROJECT_ROOT)
#                 st.download_button(
#                     label="⬇️ Download Project ZIP",
#                     data=zip_bytes,
#                     file_name="generated_project.zip",
#                     mime="application/zip",
#                     use_container_width=True,
#                 )
#             else:
#                 st.warning("⚠️ No generated project files found to download.")

#         except Exception as e:
#             st.error("❌ An error occurred while running the agent.")
#             st.exception(e)
#             st.text("Detailed Traceback:")
#             st.code(traceback.format_exc(), language="python")


# if __name__ == "__main__":
#     main()

import streamlit as st
import traceback
import shutil
import tempfile
import os
from pathlib import Path

from agent.graph import build_agent, init_project_root


def zip_project_folder(project_path: str):
    """Create a ZIP file of the given project folder and return its path."""
    project_dir = Path(project_path)
    if not project_dir.exists():
        st.warning("⚠️ No project generated yet.")
        return None

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{project_dir.name}.zip")
    shutil.make_archive(zip_path.replace(".zip", ""), "zip", project_dir)
    return zip_path


def main():
    # -------------------------------
    # Page Configuration
    # -------------------------------
    st.set_page_config(
        page_title="AI Project Generator",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 AI Project Generator")
    st.write(
        "Generate, plan, and download your AI or engineering project using an "
        "agentic workflow powered by **LangGraph + Groq**."
    )

    # -------------------------------
    # Sidebar Settings
    # -------------------------------
    with st.sidebar:
        st.header("⚙️ Settings")

        api_key = st.text_input(
            "🔑 Enter your Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Your Groq API key is used only for this session and not stored."
        )

        recursion_limit = st.number_input(
            "Recursion Limit",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            help="Limit for recursion depth during processing."
        )

        project_name = st.text_input(
            "🧱 Project Name (optional)",
            placeholder="my_ai_app",
            help="Your project will be saved under this name with a unique timestamp."
        )

    # -------------------------------
    # Main Input
    # -------------------------------
    user_prompt = st.text_area(
        "🧾 Enter your project idea or description",
        placeholder="e.g. Build a web-based calculator app using Flask",
        height=150
    )

    # -------------------------------
    # Run Agent Button
    # -------------------------------
    if st.button("🚀 Generate Project", use_container_width=True):
        if not user_prompt.strip():
            st.warning("Please enter a project description first.")
            st.stop()
        if not api_key.strip():
            st.warning("Please enter your Groq API key.")
            st.stop()

        try:
            # Initialize a unique project directory
            st.info("🧱 Initializing project structure...")
            project_path = init_project_root(project_name or "project")

            # Build and run the agent
            st.info("🤖 Running agent... This may take a few minutes ⏳")
            agent = build_agent(api_key)

            with st.spinner("Processing your request..."):
                result = agent.invoke(
                    {"user_prompt": user_prompt},
                    {"recursion_limit": recursion_limit}
                )

            # Display results
            st.success("✅ Project generation completed successfully!")
            st.subheader("📋 Final State:")
            st.json(result)

            # -------------------------------
            # Create ZIP for Download
            # -------------------------------
            st.info("📦 Packaging your project files...")
            zip_path = zip_project_folder(project_path)

            if zip_path:
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Project ZIP",
                        data=f,
                        file_name=f"{Path(project_path).name}.zip",
                        mime="application/zip",
                        use_container_width=True,
                    )
                st.success("Your project is ready to download!")
            else:
                st.warning("⚠️ No project files found to zip.")

        except Exception as e:
            st.error("An unexpected error occurred during project generation.")
            st.exception(e)
            st.text("Detailed Traceback:")
            st.code(traceback.format_exc(), language="python")


# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    main()
