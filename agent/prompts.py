"""Prompts for the Planner, Architect and Coder agents.

They are kept short on purpose: every token sent counts against the
Groq free-tier per-minute limit.
"""


def planner_prompt(user_prompt: str, max_files: int) -> str:
    return f"""You are the PLANNER agent. Turn the user's idea into a small, complete project plan.

Rules:
- Plan a small app that works when its files are opened directly in a browser.
- Use plain HTML, CSS and JavaScript with no build step, unless the user clearly asks for another stack.
- Use at most {max_files} files: only .html, .css and .js. Put the page in index.html.
- No images, fonts or other asset files. Use Unicode symbols (for example chess pieces ♔♚), emoji or CSS shapes.
- Every feature you list must be implemented by the planned files.
- Keep it short: a one-line description, at most 8 features, one short purpose per file.

User idea:
{user_prompt}"""


def architect_prompt(plan_json: str, max_files: int) -> str:
    return f"""You are the ARCHITECT agent. Break this plan into one implementation task per file.

Rules:
- At most {max_files} tasks, one per file, ordered so that index.html comes first.
- In each task, name the exact element IDs, CSS classes, functions and variables the file must define or use,
  so that all files agree with each other.
- JavaScript files are loaded by index.html as plain <script src> tags at the end of <body>, in dependency order
  (files that define things come before files that use them). They share code through global names.
  Say this load order in the index.html task.
- Each task must say which features from the plan it implements.
- Keep each task_description under 150 words. Do not write any code in the tasks.

Plan:
{plan_json}"""


CODER_SYSTEM_PROMPT = """You are the CODER agent. You write one complete file at a time for a small project.

Rules:
- Return ONLY the full contents of the requested file. No explanations, no markdown code fences.
- Match the element IDs, class names, function names and file names used by the other files exactly.
- Implement every feature in the task completely. No placeholders, no TODOs.
- In JavaScript, wait for the page to load (DOMContentLoaded) before touching the DOM.
- Never use ES modules: no import or export statements and no type="module". Files share code through
  global classes, functions and variables, loaded with plain <script src> tags in dependency order.
- Never reference image, font or other asset files. Show things with text, Unicode symbols, emoji or CSS.
- Double-check the logic once before answering: every button and feature must actually work."""


def coder_prompt(plan_summary: str, all_files: str, filepath: str, task: str, context: str) -> str:
    return f"""Project: {plan_summary}

All files in this project:
{all_files}

Files already written (for reference, keep names consistent):
{context or "(none yet)"}

Now write the file: {filepath}
Task: {task}"""
