# agent/graph.py

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


# agent/graph.py

# import logging
# import pathlib
# import datetime
# import uuid
# from typing import Tuple

# from langchain_groq.chat_models import ChatGroq
# from langchain.agents import create_agent

# from agent.tools import (
#     write_file,
#     read_file,
#     get_current_directory,
#     list_files,
#     safe_path_for_project,
# )

# from langgraph.constants import END
# from langgraph.graph import StateGraph
# from agent import tools
# from agent.prompts import *
# from agent.states import *


# # -------------------------------
# # Setup logging
# # -------------------------------
# logging.basicConfig(level=logging.INFO)


# # -------------------------------
# # Project folder management
# # -------------------------------
# # Vercel note: only /tmp is writable
# BASE_PROJECTS_DIR = pathlib.Path("/tmp/generated_projects")
# BASE_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


# def init_project_root(app_name: str = "project") -> str:
#     """Create a unique folder for each generated project safely inside /tmp."""
#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     safe_name = "".join(c if c.isalnum() else "_" for c in app_name)[:30] or "project"

#     project_root = BASE_PROJECTS_DIR / f"{safe_name}_{timestamp}_{uuid.uuid4().hex[:6]}"
#     project_root.mkdir(parents=True, exist_ok=True)

#     tools.set_project_root(project_root)
#     logging.info(f"Initialized new project folder at {project_root}")

#     return str(project_root)


# # -------------------------------
# # LLM Setup
# # -------------------------------
# def get_llm(api_key: str):
#     """Return ChatGroq LLM instance using provided API key."""
#     if not api_key or not api_key.startswith("gsk_"):
#         raise ValueError("Invalid or missing Groq API key.")

#     try:
#         return ChatGroq(model="openai/gpt-oss-120b", groq_api_key=api_key)
#     except Exception as e:
#         logging.error(f"Failed to initialize ChatGroq: {e}")
#         raise RuntimeError("Unable to connect to Groq API. Please check your key or network.")


# # -------------------------------
# # Build LangGraph Agent
# # -------------------------------
# def build_agent(api_key: str):
#     """Build and return the LangGraph workflow."""
#     llm = get_llm(api_key)
#     shared_tools = [read_file, write_file, list_files, get_current_directory]

#     # -------------------------------
#     # Planner Node
#     # -------------------------------
#     def planner_agent(state: dict) -> dict:
#         user_prompt = state["user_prompt"]
#         resp = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
#         if resp is None:
#             raise ValueError("Planner did not return a valid response.")
#         return {"plan": resp}

#     # -------------------------------
#     # Architect Node
#     # -------------------------------
#     def architect_agent(state: dict) -> dict:
#         plan: Plan = state["plan"]
#         resp = llm.with_structured_output(TaskPlan).invoke(
#             architect_prompt(plan=plan.model_dump_json())
#         )
#         if resp is None:
#             raise ValueError("Architect did not return a valid response.")
#         resp.plan = plan
#         return {"task_plan": resp}

#     # -------------------------------
#     # Coder Node
#     # -------------------------------
#     def coder_agent(state: dict) -> dict:
#         coder_state: CoderState = state.get("coder_state") or CoderState(
#             task_plan=state["task_plan"], current_step_idx=0
#         )
#         steps = coder_state.task_plan.implementation_steps

#         if coder_state.current_step_idx >= len(steps):
#             return {"coder_state": coder_state, "status": "DONE"}

#         current_task = steps[coder_state.current_step_idx]
#         existing_content = read_file.run(current_task.filepath)
#         system_prompt = coder_system_prompt()

#         user_prompt = (
#             f"Task: {current_task.task_description}\n"
#             f"File: {current_task.filepath}\n"
#             f"Existing content:\n{existing_content}\n"
#             "Use write_file(path, content) to save your changes."
#         )

#         react_agent = create_agent(llm, shared_tools)
#         react_agent.invoke(
#             {
#                 "messages": [
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": user_prompt},
#                 ]
#             }
#         )

#         coder_state.current_step_idx += 1
#         return {"coder_state": coder_state}

#     # -------------------------------
#     # Build LangGraph flow
#     # -------------------------------
#     graph = StateGraph(dict)
#     graph.add_node("planner", planner_agent)
#     graph.add_node("architect", architect_agent)
#     graph.add_node("coder", coder_agent)

#     graph.add_edge("planner", "architect")
#     graph.add_edge("architect", "coder")
#     graph.add_conditional_edges(
#         "coder",
#         lambda s: "END" if s.get("status") == "DONE" else "coder",
#         {"END": END, "coder": "coder"},
#     )
#     graph.set_entry_point("planner")

#     return graph.compile()


# agent/graph.py

