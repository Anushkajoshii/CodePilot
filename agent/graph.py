"""CodePilot: a three-agent LangGraph pipeline (Planner -> Architect -> Coder).

Token-saving design for the Groq free tier:
- Planner and Architect each make one structured-output call.
- The Coder makes one plain call per file (no tool-calling loop), seeing only a
  trimmed view of files already written.
- Rate limits are handled by waiting and retrying; retired models fall back to the next one.
"""
import datetime
import logging
import os
import pathlib
import uuid
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph

from agent import tools
from agent.codegen import build_context, call_with_fallback, call_with_retry, strip_code_fences
from agent.prompts import CODER_SYSTEM_PROMPT, architect_prompt, coder_prompt, planner_prompt
from agent.states import Plan, TaskPlan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models are tried in order; override with comma-separated env vars.
PLANNER_MODELS = [m.strip() for m in os.environ.get(
    "CODEPILOT_PLANNER_MODELS", "openai/gpt-oss-120b,llama-3.3-70b-versatile").split(",") if m.strip()]
CODER_MODELS = [m.strip() for m in os.environ.get(
    "CODEPILOT_CODER_MODELS", "llama-3.3-70b-versatile,openai/gpt-oss-20b,llama-3.1-8b-instant").split(",") if m.strip()]
MAX_IMPLEMENTATION_STEPS = int(os.environ.get("CODEPILOT_MAX_STEPS", "5"))
MAX_FILE_TOKENS = int(os.environ.get("CODEPILOT_MAX_FILE_TOKENS", "3000"))

BASE_PROJECTS_DIR = pathlib.Path.cwd() / "generated_projects"


class GraphState(TypedDict, total=False):
    """Shared state: each node returns only the keys it changes."""
    user_prompt: str
    plan: Plan
    task_plan: TaskPlan
    step: int
    written: dict


def init_project_root(app_name: str = "project") -> str:
    """Create a unique folder for one generated project and sandbox file writes to it."""
    BASE_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in app_name)[:30] or "project"
    root = BASE_PROJECTS_DIR / f"{safe_name}_{timestamp}_{uuid.uuid4().hex[:6]}"
    root.mkdir(parents=True, exist_ok=True)
    tools.set_project_root(root)
    logger.info("Initialized project folder at %s", root)
    return str(root)


def get_llm(api_key: str, model: str, max_tokens: int | None = None) -> ChatGroq:
    # Retries are handled in call_with_retry so we can respect Groq's "try again in Xs".
    return ChatGroq(model=model, api_key=api_key, max_retries=0, timeout=90, max_tokens=max_tokens, temperature=0.2)


def build_agent(api_key: str, llm_factory=get_llm, on_event=None):
    """Build the LangGraph workflow.

    llm_factory(api_key, model, max_tokens) -> chat model; injectable for tests.
    on_event(kind, detail) is an optional progress callback for the UI.
    """
    def emit(kind: str, detail: str = "") -> None:
        if on_event:
            on_event(kind, detail)

    def wait_note(seconds: float) -> None:
        emit("waiting", f"Groq rate limit reached, waiting {seconds:.0f}s and retrying...")

    def structured(models, schema, prompt):
        def make_call(model):
            llm = llm_factory(api_key, model, None).with_structured_output(schema)
            return call_with_retry(lambda: llm.invoke(prompt), on_wait=wait_note)
        result = call_with_fallback(models, make_call)
        if result is None:
            raise ValueError(f"The model returned no {schema.__name__}.")
        return result

    def planner_agent(state: dict) -> dict:
        emit("stage", "Planner is designing the app...")
        plan = structured(PLANNER_MODELS, Plan, planner_prompt(state["user_prompt"], MAX_IMPLEMENTATION_STEPS))
        return {"plan": plan}

    def architect_agent(state: dict) -> dict:
        emit("stage", "Architect is breaking the plan into files...")
        plan: Plan = state["plan"]
        task_plan = structured(
            PLANNER_MODELS, TaskPlan, architect_prompt(plan.model_dump_json(), MAX_IMPLEMENTATION_STEPS))
        # One task per file, capped, so a run stays fast and inside free-tier limits.
        seen, steps = set(), []
        for step in task_plan.implementation_steps:
            if step.filepath not in seen:
                seen.add(step.filepath)
                steps.append(step)
        task_plan.implementation_steps = steps[:MAX_IMPLEMENTATION_STEPS]
        if not task_plan.implementation_steps:
            raise ValueError("The architect produced no files to write.")
        return {"task_plan": task_plan, "step": 0, "written": {}}

    def coder_agent(state: dict) -> dict:
        plan: Plan = state["plan"]
        steps = state["task_plan"].implementation_steps
        idx = state["step"]
        task = steps[idx]
        emit("file", f"Coder is writing {task.filepath} ({idx + 1}/{len(steps)})")

        all_files = "\n".join(f"- {s.filepath}: {s.task_description[:160]}" for s in steps)
        summary = f"{plan.name}: {plan.description}. Features: {'; '.join(plan.features)}"
        messages = [
            SystemMessage(content=CODER_SYSTEM_PROMPT),
            HumanMessage(content=coder_prompt(
                summary, all_files, task.filepath, task.task_description, build_context(state["written"]))),
        ]

        def make_call(model):
            llm = llm_factory(api_key, model, MAX_FILE_TOKENS)
            return call_with_retry(lambda: llm.invoke(messages), on_wait=wait_note)

        response = call_with_fallback(CODER_MODELS, make_call)
        content = strip_code_fences(getattr(response, "content", str(response)))
        tools.write_file(task.filepath, content)
        written = {**state["written"], task.filepath: content}
        return {"written": written, "step": idx + 1}

    graph = StateGraph(GraphState)
    graph.add_node("planner", planner_agent)
    graph.add_node("architect", architect_agent)
    graph.add_node("coder", coder_agent)
    graph.set_entry_point("planner")
    graph.add_edge("planner", "architect")
    graph.add_edge("architect", "coder")
    graph.add_conditional_edges(
        "coder",
        lambda s: END if s["step"] >= len(s["task_plan"].implementation_steps) else "coder",
    )
    return graph.compile()
