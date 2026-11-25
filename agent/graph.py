"""CodePilot: a three-agent LangGraph pipeline (Planner -> Architect -> Coder).

Token-saving design for the Groq free tier:
- Planner and Architect each make one structured-output call.
- The Coder makes one plain call per file (no tool-calling loop), seeing only a
  trimmed view of files already written.
- Rate limits are handled by waiting and retrying; retired models fall back to the next one.
"""
import datetime
import json
import logging
import os
import pathlib
import uuid
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph

from agent import tools
from agent.codegen import (
    BadOutputError, build_context, call_with_fallback, call_with_retry, find_missing_files, is_bad_output,
    make_browser_safe_html, make_browser_safe_js, strip_code_fences,
)
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
    warnings: list


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
        """Get a Pydantic object from the model.

        Models sometimes answer in prose instead of calling the schema tool
        (Groq then returns 400 'tool_use_failed'). For each model we try tool
        calling first, then plain JSON mode; if both fail, the next model.
        """
        json_prompt = (
            prompt
            + "\n\nRespond with ONLY a JSON object (no markdown, no prose) that matches this JSON schema:\n"
            + json.dumps(schema.model_json_schema())
        )
        attempts = (("function_calling", prompt), ("json_mode", json_prompt))

        def make_call(model):
            last_exc = None
            for method, text in attempts:
                try:
                    llm = llm_factory(api_key, model, None).with_structured_output(schema, method=method)
                    result = call_with_retry(lambda llm=llm, text=text: llm.invoke(text), on_wait=wait_note)
                    if result is not None:
                        return result
                    last_exc = BadOutputError(f"{model} returned no {schema.__name__}")
                except Exception as exc:  # noqa: BLE001
                    if not is_bad_output(exc):
                        raise
                    logger.warning("%s gave unusable %s output via %s: %s", model, schema.__name__, method, exc)
                    last_exc = exc
                emit("retry", f"Reformatting the {schema.__name__} answer and trying again...")
            raise BadOutputError(f"{model} could not produce a valid {schema.__name__}") from last_exc

        return call_with_fallback(models, make_call)

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
                summary, all_files, task.filepath, task.task_description, build_context(state["written"], max_chars=8000))),
        ]

        def make_call(model):
            llm = llm_factory(api_key, model, MAX_FILE_TOKENS)
            return call_with_retry(lambda: llm.invoke(messages), on_wait=wait_note)

        response = call_with_fallback(CODER_MODELS, make_call)
        content = strip_code_fences(getattr(response, "content", str(response)))
        tools.write_file(task.filepath, content)
        written = {**state["written"], task.filepath: content}
        return {"written": written, "step": idx + 1}

    def checker_agent(state: dict) -> dict:
        """Fix common browser problems in the generated files and report anything still missing."""
        emit("stage", "Checking the files work together in a browser...")
        written = dict(state["written"])
        fixed = []
        for path, content in written.items():
            if path.endswith(".js"):
                new, changed = make_browser_safe_js(content)
            elif path.endswith(".html"):
                new, changed = make_browser_safe_html(content)
            else:
                continue
            if changed:
                tools.write_file(path, new)
                written[path] = new
                fixed.append(path)
        warnings = []
        if fixed:
            warnings.append("Converted module syntax (import/export) to plain scripts in: " + ", ".join(fixed))
        missing = find_missing_files(written)
        if missing:
            warnings.append("These files are referenced but were not generated: " + ", ".join(missing))
        return {"written": written, "warnings": warnings}

    graph = StateGraph(GraphState)
    graph.add_node("planner", planner_agent)
    graph.add_node("architect", architect_agent)
    graph.add_node("coder", coder_agent)
    graph.add_node("checker", checker_agent)
    graph.set_entry_point("planner")
    graph.add_edge("planner", "architect")
    graph.add_edge("architect", "coder")
    graph.add_conditional_edges(
        "coder",
        lambda s: "checker" if s["step"] >= len(s["task_plan"].implementation_steps) else "coder",
    )
    graph.add_edge("checker", END)
    return graph.compile()
