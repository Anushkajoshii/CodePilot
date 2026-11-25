"""Run the whole Planner -> Architect -> Coder graph with a fake LLM (no network)."""
from langchain_core.messages import AIMessage

from agent import graph as g
from agent.states import File, ImplementationTask, Plan, TaskPlan

PLAN = Plan(name="Counter", description="A click counter", techstack="html, css, javascript",
            features=["increment", "reset"],
            files=[File(path="index.html", purpose="page"), File(path="app.js", purpose="logic")])
TASKS = TaskPlan(implementation_steps=[
    ImplementationTask(filepath="index.html", task_description="Page with #count, #inc, #reset; loads app.js"),
    ImplementationTask(filepath="app.js", task_description="Increment and reset handlers"),
    ImplementationTask(filepath="app.js", task_description="duplicate step that should be dropped"),
])


class FakeLLM:
    def __init__(self, model, log):
        self.model, self.log, self.schema = model, log, None

    def with_structured_output(self, schema, method="function_calling"):
        self.schema, self.method = schema, method
        return self

    def invoke(self, prompt):
        self.log.append((self.model, getattr(self, "method", None)))
        if self.schema is TaskPlan and self.model == "prose" :
            # Simulates Groq's 400 when the model writes markdown instead of calling the tool
            raise Exception("Error code: 400 - {'error': {'code': 'tool_use_failed', "
                            "'message': 'Tool choice is required, but model did not call a tool'}}")
        if self.schema is TaskPlan and self.method == "function_calling" and self.model == "flaky":
            raise Exception("Error code: 400 - tool_use_failed")
        if self.schema is Plan:
            return PLAN
        if self.schema is TaskPlan:
            return TASKS.model_copy(deep=True)
        if self.model == "retired":
            raise Exception("model_decommissioned")
        return AIMessage(content="```\n// file for prompt\n```")


def test_full_graph_writes_each_file_once(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "BASE_PROJECTS_DIR", tmp_path)
    monkeypatch.setattr(g, "CODER_MODELS", ["retired", "good"])
    log, events = [], []
    root = g.init_project_root("counter")
    agent = g.build_agent("key", llm_factory=lambda k, m, t: FakeLLM(m, log),
                          on_event=lambda kind, d: events.append(kind))
    state = agent.invoke({"user_prompt": "a click counter"})
    assert set(state["written"]) == {"index.html", "app.js"}
    assert (tmp_path / root.split("/")[-1] / "app.js").read_text() == "// file for prompt\n"
    assert any(m == "good" for m, _ in log)  # fell back from the retired model
    assert events.count("file") == 2


def test_architect_recovers_when_model_answers_in_prose(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "BASE_PROJECTS_DIR", tmp_path)
    monkeypatch.setattr(g, "CODER_MODELS", ["good"])
    log = []
    g.init_project_root("x")

    # 'flaky' fails tool calling but succeeds in JSON mode
    monkeypatch.setattr(g, "PLANNER_MODELS", ["flaky"])
    state = g.build_agent("k", llm_factory=lambda k, m, t: FakeLLM(m, log)).invoke({"user_prompt": "x"})
    assert ("flaky", "json_mode") in log and len(state["written"]) == 2

    # 'prose' fails both ways for TaskPlan, so the next model takes over
    log.clear()
    monkeypatch.setattr(g, "PLANNER_MODELS", ["prose", "good"])
    state = g.build_agent("k", llm_factory=lambda k, m, t: FakeLLM(m, log)).invoke({"user_prompt": "x"})
    assert ("prose", "json_mode") in log and ("good", "function_calling") in log
    assert len(state["written"]) == 2
