# 🚀 CodePilot

**CodePilot** is your AI-powered developer buddy — built with **LangGraph**, **LangChain**, and **Groq Cloud**.  
It acts like a multi-agent development team that can take a natural language request such as  
_“Build a calculator web app”_ and automatically generate a **complete, working project** — file by file — just like a real coder.

---

## 🧠 Architecture

CodePilot uses a **multi-agent architecture** to simulate real-world software development workflows:

- **🗺️ Planner Agent** — Understands your prompt and creates a detailed project roadmap.  
- **🏗️ Architect Agent** — Breaks the roadmap into granular engineering tasks and assigns responsibilities for each file.  
- **💻 Coder Agent** — Implements those tasks, writes code files, and executes necessary commands to assemble the project.  


---

## ⚙️ Tech Stack

| Component | Description |
|------------|-------------|
| 🧩 **LangGraph** | For orchestrating agent workflows |
| 🧠 **LangChain** | For structured LLM reasoning and tool usage |
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

- “Build a to-do list web app using React and FastAPI.”

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