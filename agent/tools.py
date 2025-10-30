# # agent/tools.py
# import pathlib
# import subprocess
# from typing import Tuple
# from langchain_core.tools import tool, StructuredTool


# PROJECT_ROOT: pathlib.Path | None = None


# def set_project_root(root: pathlib.Path):
#     """Allow external modules (like graph.py) to set the global project root."""
#     global PROJECT_ROOT
#     PROJECT_ROOT = root


# def safe_path_for_project(path: str) -> pathlib.Path:
#     """Ensure the given path stays within the PROJECT_ROOT sandbox."""
#     if PROJECT_ROOT is None:
#         raise RuntimeError("PROJECT_ROOT not initialized — call set_project_root() first.")
    
#     p = pathlib.Path(path).expanduser()
#     if not p.is_absolute():
#         p = (PROJECT_ROOT / p).resolve()

#     # If absolute but inside PROJECT_ROOT, allow it
#     project_root_resolved = PROJECT_ROOT.resolve()
#     if not str(p).startswith(str(project_root_resolved)):
#         raise ValueError(f"Attempt to access path outside project root: {p}")

#     return p



# # -------------------------------
# # TOOLS
# # -------------------------------

# @tool
# def write_file(path: str, content: str) -> str:
#     """Writes content to a file inside the project root."""
#     p = safe_path_for_project(path)
#     p.parent.mkdir(parents=True, exist_ok=True)
#     p.write_text(content, encoding="utf-8")
#     return f"WROTE: {p}"


# @tool
# def read_file(path: str) -> str:
#     """Reads content from a file inside the project root."""
#     p = safe_path_for_project(path)
#     return p.read_text(encoding="utf-8") if p.exists() else ""


# @tool
# def get_current_directory() -> str:
#     """Returns the current project root path."""
#     return str(PROJECT_ROOT)


# # define the plain Python function separately
# def _list_files(directory: str = ".") -> str:
#     """Lists all files in the specified directory within the project root."""
#     p = safe_path_for_project(directory)
#     if not p.is_dir():
#         return f"ERROR: {p} is not a directory"
#     files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]
#     return "\n".join(files) if files else "No files found."


# # now create both variants safely
# list_files = tool(_list_files)
# list_file = StructuredTool.from_function(_list_files)


# @tool
# def run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> Tuple[int, str, str]:
#     """Runs a shell command in the specified directory and returns code, stdout, stderr."""
#     cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT
#     res = subprocess.run(
#         cmd, shell=True, cwd=str(cwd_dir),
#         capture_output=True, text=True, timeout=timeout
#     )
#     return res.returncode, res.stdout, res.stderr


# def init_project_root() -> str:
#     """Initialize and return the project root path."""
#     PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
#     return str(PROJECT_ROOT)


import pathlib
import subprocess
from pydantic import BaseModel, Field

# ✅ Import StructuredTool safely for both environments
try:
    from langchain_core.tools import StructuredTool
except ImportError:
    from langchain.tools import StructuredTool


PROJECT_ROOT: pathlib.Path | None = None

def set_project_root(root: pathlib.Path):
    """Allow external modules (like graph.py) to set the global project root."""
    global PROJECT_ROOT
    PROJECT_ROOT = root.resolve()
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)



# ------------------------------------------------------------------
# Utility: Safe path handling
# ------------------------------------------------------------------
def safe_path_for_project(path: str) -> pathlib.Path:
    if PROJECT_ROOT is None:
        raise RuntimeError("PROJECT_ROOT not initialized — call set_project_root() first.")

    p = pathlib.Path(path).expanduser()
    if not p.is_absolute():
        p = (PROJECT_ROOT / p).resolve()

    project_root_resolved = PROJECT_ROOT.resolve()
    if not str(p).startswith(str(project_root_resolved)):
        raise ValueError(f"Attempt to access path outside project root: {p}")

    return p



# ------------------------------------------------------------------
# Tool 1: Write File
# ------------------------------------------------------------------
class WriteFileInput(BaseModel):
    path: str = Field(..., description="Path relative to project root.")
    content: str = Field(..., description="File contents to write.")



def write_file(path: str, content: str) -> str:
    """Write content to a file safely inside the project root."""
    file_path = safe_path_for_project(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Wrote file: {file_path}"

write_file = StructuredTool(
    name="write_file",
    description="Write text content to a file inside the project folder.",
    func=_write_file,
    args_schema=WriteFileInput,
)


# ------------------------------------------------------------------
# Tool 2: Read File
# ------------------------------------------------------------------
class ReadFileInput(BaseModel):
    path: str = Field(..., description="Path of file to read relative to project root.")


def read_file(path: str) -> str:
    file_path = safe_path_for_project(path)
    if not file_path.exists():
        return f"❌ File not found: {path}"
    return file_path.read_text(encoding="utf-8")


read_file = StructuredTool(
    name="read_file",
    description="Read a file from the project folder.",
    func=_read_file,
    args_schema=ReadFileInput,
)


# ------------------------------------------------------------------
# Tool 3: List Files (✅ FIXED SCHEMA)
# ------------------------------------------------------------------
class ListFilesInput(BaseModel):
    path: str = Field(default=".", description="Path relative to project root to list files from.")


def list_files(path: str = ".") -> str:
    p = safe_path_for_project(path)
    if not p.exists():
        return f"❌ Path not found: {path}"
    if not p.is_dir():
        return f"⚠️ {path} is not a directory"
    files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]
    return "\n".join(files) if files else "📁 No files found."


list_files = StructuredTool(
    name="list_files",
    description="List all files inside the project folder.",
    func=_list_files,
    args_schema=ListFilesInput,
)


# ------------------------------------------------------------------
# Tool 4: Get Current Directory
# ------------------------------------------------------------------

def get_current_directory() -> str:
    return str(PROJECT_ROOT.resolve())


get_current_directory = StructuredTool.from_function(
    func=_get_current_directory,
    name="get_current_directory",
    description="Return the current working directory for the project.",
)


# ------------------------------------------------------------------
# Tool 5: Run Command (optional)
# ------------------------------------------------------------------
class RunCommandInput(BaseModel):
    command: str = Field(..., description="Shell command to execute inside the project root.")


def run_command(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60)
        return result.stdout or result.stderr or "✅ Command executed successfully (no output)."
    except Exception as e:
        return f"❌ Command failed: {e}"


run_command = StructuredTool(
    name="run_command",
    description="Run a shell command inside the project directory.",
    func=_run_command,
    args_schema=RunCommandInput,
)
