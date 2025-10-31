# from dotenv import load_dotenv
# import logging
# from langchain_groq.chat_models import ChatGroq
# from langgraph.constants import END
# from langgraph.graph import StateGraph
# # from langgraph.prebuilt import create_react_agent
# from langchain.agents import create_agent



# from agent.prompts import *
# from agent.states import *
# from agent.tools import write_file, read_file, get_current_directory, list_files

# _ = load_dotenv()

# logging.basicConfig(level=logging.DEBUG)

# llm = ChatGroq(model="openai/gpt-oss-120b")


# def planner_agent(state: dict) -> dict:
#     """Converts user prompt into a structured Plan."""
#     user_prompt = state["user_prompt"]
#     resp = llm.with_structured_output(Plan).invoke(
#         planner_prompt(user_prompt)
#     )
#     if resp is None:
#         raise ValueError("Planner did not return a valid response.")
#     return {"plan": resp}


# def architect_agent(state: dict) -> dict:
#     """Creates TaskPlan from Plan."""
#     plan: Plan = state["plan"]
#     resp = llm.with_structured_output(TaskPlan).invoke(
#         architect_prompt(plan=plan.model_dump_json())
#     )
#     if resp is None:
#         raise ValueError("Planner did not return a valid response.")

#     resp.plan = plan
#     print(resp.model_dump_json())
#     return {"task_plan": resp}


# def coder_agent(state: dict) -> dict:
#     """LangGraph tool-using coder agent."""
#     coder_state: CoderState = state.get("coder_state")
#     if coder_state is None:
#         coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

#     steps = coder_state.task_plan.implementation_steps
#     if coder_state.current_step_idx >= len(steps):
#         return {"coder_state": coder_state, "status": "DONE"}

#     current_task = steps[coder_state.current_step_idx]
#     existing_content = read_file.run(current_task.filepath)

#     system_prompt = coder_system_prompt()
#     user_prompt = (
#         f"Task: {current_task.task_description}\n"
#         f"File: {current_task.filepath}\n"
#         f"Existing content:\n{existing_content}\n"
#         "Use write_file(path, content) to save your changes."
#     )

#     coder_tools = [read_file, write_file, list_files, get_current_directory]
#     # react_agent = create_react_agent(llm, coder_tools)
#     react_agent = create_agent(llm, coder_tools)

#     react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
#                                      {"role": "user", "content": user_prompt}]})

#     coder_state.current_step_idx += 1
#     return {"coder_state": coder_state}


# graph = StateGraph(dict)

# graph.add_node("planner", planner_agent)
# graph.add_node("architect", architect_agent)
# graph.add_node("coder", coder_agent)

# graph.add_edge("planner", "architect")
# graph.add_edge("architect", "coder")
# graph.add_conditional_edges(
#     "coder",
#     lambda s: "END" if s.get("status") == "DONE" else "coder",
#     {"END": END, "coder": "coder"}
# )

# graph.set_entry_point("planner")
# agent = graph.compile()
# # user_prompt = "Build a colourful modern todo app in html css and js"
# # result = agent.invoke({"user_prompt": user_prompt})
# # print("Final State:", result)
# # Build a colourful modern todo app in html css and js
# # Create a simple calculator web application


# if __name__ == "__main__":
#     result = agent.invoke({"user_prompt": "Build a colourful modern todo app in html css and js"},
#                           {"recursion_limit": 100})
#     print("Final State:", result)



import logging
import pathlib
import subprocess
import datetime
import uuid
from typing import Tuple

from langchain_groq.chat_models import ChatGroq
from langchain.agents import create_agent

from agent.tools import write_file, read_file, get_current_directory, list_files, safe_path_for_project

from langgraph.constants import END
from langgraph.graph import StateGraph
from agent import tools
from agent.prompts import *
from agent.states import *


# -------------------------------
# Setup logging
# -------------------------------
logging.basicConfig(level=logging.INFO)


# -------------------------------
# Project folder management
# -------------------------------
BASE_PROJECTS_DIR = pathlib.Path.cwd() / "generated_projects"
BASE_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_ROOT: pathlib.Path = None  # will be set each run


def init_project_root(app_name: str = "project") -> str:
    """Create a unique folder for each generated project."""
    global PROJECT_ROOT

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in app_name)[:30] or "project"
    PROJECT_ROOT = BASE_PROJECTS_DIR / f"{safe_name}_{timestamp}_{uuid.uuid4().hex[:6]}"
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    
    tools.set_project_root(PROJECT_ROOT)

    logging.info(f"Initialized new project folder at {PROJECT_ROOT}")
    return str(PROJECT_ROOT)


# def safe_path_for_project(path: str) -> pathlib.Path:
#     """Ensure the path stays inside PROJECT_ROOT."""
#     if PROJECT_ROOT is None:
#         raise RuntimeError("PROJECT_ROOT not initialized — call init_project_root() first.")
#     p = (PROJECT_ROOT / path).resolve()
#     if not p.is_relative_to(PROJECT_ROOT.resolve()):
#         raise ValueError(f"Attempt to access path outside project root: {p}")
#     return p


# # -------------------------------
# # File Tools
# # -------------------------------
# @tool
# def write_file(path: str, content: str) -> str:
#     """Writes content to a file inside the project folder."""
#     p = safe_path_for_project(path)
#     p.parent.mkdir(parents=True, exist_ok=True)
#     with open(p, "w", encoding="utf-8") as f:
#         f.write(content)
#     return f"WROTE: {p}"


# @tool
# def read_file(path: str) -> str:
#     """Reads content from a file inside the project folder."""
#     p = safe_path_for_project(path)
#     return p.read_text(encoding="utf-8") if p.exists() else ""


# @tool
# def list_files(directory: str = ".") -> str:
#     """Lists all files inside the project folder."""
#     p = safe_path_for_project(directory)
#     if not p.is_dir():
#         return f"ERROR: {p} is not a directory"
#     return "\n".join(str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()) or "No files found."


# @tool
# def get_current_directory() -> str:
#     """Returns the current project folder path."""
#     return str(PROJECT_ROOT)


# @tool
# def run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> Tuple[int, str, str]:
#     """Run a shell command in the project folder."""
#     cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT
#     res = subprocess.run(
#         cmd, shell=True, cwd=str(cwd_dir),
#         capture_output=True, text=True, timeout=timeout
#     )
#     return res.returncode, res.stdout, res.stderr


# -------------------------------
# LLM Setup
# -------------------------------
def get_llm(api_key: str):
    """Return ChatGroq LLM instance using provided API key."""
    return ChatGroq(model="openai/gpt-oss-120b", groq_api_key=api_key)


# -------------------------------
# Build LangGraph Agent
# -------------------------------
def build_agent(api_key: str):
    """Build and return the LangGraph workflow."""
    llm = get_llm(api_key)
    shared_tools = [read_file, write_file, list_files, get_current_directory]

    def planner_agent(state: dict) -> dict:
        user_prompt = state["user_prompt"]
        resp = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
        if resp is None:
            raise ValueError("Planner did not return a valid response.")
        return {"plan": resp}

    def architect_agent(state: dict) -> dict:
        plan: Plan = state["plan"]
        resp = llm.with_structured_output(TaskPlan).invoke(architect_prompt(plan=plan.model_dump_json()))
        if resp is None:
            raise ValueError("Architect did not return a valid response.")
        resp.plan = plan
        return {"task_plan": resp}

    def coder_agent(state: dict) -> dict:
        coder_state: CoderState = state.get("coder_state") or CoderState(task_plan=state["task_plan"], current_step_idx=0)
        steps = coder_state.task_plan.implementation_steps

        if coder_state.current_step_idx >= len(steps):
            return {"coder_state": coder_state, "status": "DONE"}

        current_task = steps[coder_state.current_step_idx]
        existing_content = read_file.run(current_task.filepath)
        system_prompt = coder_system_prompt()

        user_prompt = (
            f"Task: {current_task.task_description}\n"
            f"File: {current_task.filepath}\n"
            f"Existing content:\n{existing_content}\n"
            "Use write_file(path, content) to save your changes."
        )

        react_agent = create_agent(llm, shared_tools)
        react_agent.invoke({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        })

        coder_state.current_step_idx += 1
        return {"coder_state": coder_state}

    # -------------------------------
    # Build LangGraph flow
    # -------------------------------
    graph = StateGraph(dict)
    graph.add_node("planner", planner_agent)
    graph.add_node("architect", architect_agent)
    graph.add_node("coder", coder_agent)

    graph.add_edge("planner", "architect")
    graph.add_edge("architect", "coder")
    graph.add_conditional_edges(
        "coder",
        lambda s: "END" if s.get("status") == "DONE" else "coder",
        {"END": END, "coder": "coder"}
    )
    graph.set_entry_point("planner")

    return graph.compile()
