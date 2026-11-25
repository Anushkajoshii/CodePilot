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

    def with_structured_output(self, schema):
        self.schema = schema
        return self

    def invoke(self, prompt):
        self.log.append(self.model)
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
    assert "good" in log  # fell back from the retired model
    assert events.count("file") == 2
