# 🚀 CodePilot

**Live demo:** https://codepilott.streamlit.app (open the *See examples* tab to try it without an API key)

**CodePilot** is your AI-powered developer buddy — built with **LangGraph**, **LangChain**, and **Groq Cloud**.  
It acts like a multi-agent development team that can take a natural language request such as  
_“Build a calculator web app”_ and automatically generate a **complete, working project** — file by file — just like a real coder.

---

## 🧠 Architecture

CodePilot uses a **multi-agent architecture** to simulate real-world software development workflows:

- **🗺️ Planner Agent** — Understands your prompt and creates a detailed project roadmap.  
- **🏗️ Architect Agent** — Breaks the roadmap into granular engineering tasks and assigns responsibilities for each file.  
- **💻 Coder Agent** — Writes each file in one focused call, seeing a trimmed view of the files already written so names and IDs stay consistent.

### Built to run on the Groq free tier

- **One call per file** instead of a tool-calling loop, so a 5-file app uses a small, predictable number of tokens.
- **Rate-limit aware:** when Groq says "try again in Xs", CodePilot waits that long and retries (up to 4 times).
- **Model fallback:** if a model is retired, it moves to the next one in the list.
- **Sandboxed writes:** generated files can only be written inside their own project folder.
- **Live preview:** generated HTML/CSS/JS apps run right inside the page.


---

## ⚙️ Tech Stack

| Component | Description |
|------------|-------------|
| 🧩 **LangGraph** | For orchestrating agent workflows |
| 🧠 **LangChain Core** | Structured outputs (Pydantic) for the plan and task list |
| ⚡ **Groq API** | High-speed inference for chat-based reasoning |
| 🖥️ **Streamlit** | Clean, interactive web interface |
| 🧰 **Python 3.12+** | Core language for logic and execution |

---

## 🏁 Getting Started

### 🔧 Prerequisites

Before running CodePilot, ensure you have:
- Python **3.12+**
- A valid [Groq API key](https://console.groq.com/keys)
- `uv` or `pip` for dependency management

---

### 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Anushkajoshii/CodePilot.git
cd CodePilot
```
### Create and activate a virtual environment
``` bash
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies
``` bash
pip install -r requirements.txt
```


### ▶️ Run Locally

### 🖥️ Streamlit UI (Recommended)

```bash
streamlit run streamlit.py
```

### 💻 Or via CLI (if available)
``` bash
python main.py
```



### 💡 Example Prompts

Try these in your deployed or local app:

- “Build a quiz app with 5 questions and a final score.”

- “Create a calculator web app in HTML, CSS, and JavaScript.”

- “Build a blog API in Flask with SQLite.”

- “Generate a dashboard UI in Streamlit with data visualization.”


## 🧩 Example Flow

- Enter a natural-language description (e.g. “Build a blog app in Flask”).

- CodePilot plans, designs, and generates your project file-by-file.

- The UI packages your project into a downloadable ZIP file.

## 📦 Output

After generation, CodePilot provides:

- 🗂️ A project folder under /tmp/generated_projects (on Vercel)

- 💾 A downloadable .zip file containing your ready-to-run app

---

## ✅ Tests and CI/CD

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

GitHub Actions runs lint and tests on every push and pull request, then builds the Docker image and pushes it to GitHub Container Registry (`ghcr.io/<owner>/codepilot`) on `main`.

Run the image locally:

```bash
docker run -p 8501:8501 -e GROQ_API_KEY=your_key ghcr.io/anushkajoshii/codepilot:latest
```

### Configuration (optional environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `CODEPILOT_PLANNER_MODELS` | `openai/gpt-oss-120b,llama-3.3-70b-versatile` | Models for planning, tried in order |
| `CODEPILOT_CODER_MODELS` | `llama-3.3-70b-versatile,openai/gpt-oss-20b,llama-3.1-8b-instant` | Models for writing files, tried in order |
| `CODEPILOT_MAX_STEPS` | `5` | Maximum number of files per project |
