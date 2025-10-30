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
from typing import Tuple
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

# -------------------------------
# PROJECT ROOT HANDLING
# -------------------------------

PROJECT_ROOT: pathlib.Path | None = None


def set_project_root(root: pathlib.Path):
    """Allow external modules (like graph.py) to set the global project root."""
    global PROJECT_ROOT
    PROJECT_ROOT = root


def safe_path_for_project(path: str) -> pathlib.Path:
    """Ensure the given path stays within the PROJECT_ROOT sandbox."""
    if PROJECT_ROOT is None:
        raise RuntimeError("PROJECT_ROOT not initialized — call set_project_root() first.")
    
    p = pathlib.Path(path).expanduser()
    if not p.is_absolute():
        p = (PROJECT_ROOT / p).resolve()

    project_root_resolved = PROJECT_ROOT.resolve()
    if not str(p).startswith(str(project_root_resolved)):
        raise ValueError(f"Attempt to access path outside project root: {p}")

    return p


# -------------------------------
# TOOL INPUT SCHEMAS
# -------------------------------

class WriteFileInput(BaseModel):
    path: str = Field(..., description="Relative path of the file to write inside the project root")
    content: str = Field(..., description="Content to write into the file")

class ReadFileInput(BaseModel):
    path: str = Field(..., description="Relative path of the file to read inside the project root")

class RunCmdInput(BaseModel):
    cmd: str = Field(..., description="Command to run in shell")
    cwd: str | None = Field(None, description="Directory to run the command in")
    timeout: int = Field(30, description="Timeout in seconds")


# -------------------------------
# TOOL FUNCTIONS
# -------------------------------

def _write_file(path: str, content: str) -> str:
    p = safe_path_for_project(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"✅ WROTE: {p.relative_to(PROJECT_ROOT)}"


def _read_file(path: str) -> str:
    p = safe_path_for_project(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _get_current_directory() -> str:
    return str(PROJECT_ROOT)


def _list_files(directory: str = ".") -> str:
    p = safe_path_for_project(directory)
    if not p.is_dir():
        return f"ERROR: {p} is not a directory"
    files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]
    return "\n".join(files) if files else "No files found."


def _run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> Tuple[int, str, str]:
    cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT
    res = subprocess.run(
        cmd, shell=True, cwd=str(cwd_dir),
        capture_output=True, text=True, timeout=timeout
    )
    return res.returncode, res.stdout, res.stderr


def init_project_root() -> str:
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    return str(PROJECT_ROOT)


# -------------------------------
# STRUCTURED TOOL EXPORTS
# -------------------------------

write_file = StructuredTool.from_function(
    _write_file,
    name="write_file",
    args_schema=WriteFileInput,
    description="Write content to a file within the project directory."
)

read_file = StructuredTool.from_function(
    _read_file,
    name="read_file",
    args_schema=ReadFileInput,
    description="Read a file's content from the project directory."
)

get_current_directory = StructuredTool.from_function(
    _get_current_directory,
    name="get_current_directory",
    description="Return the current project root path."
)

list_files = StructuredTool.from_function(
    _list_files,
    name="list_files",
    description="List all files inside the project directory."
)

run_cmd = StructuredTool.from_function(
    _run_cmd,
    name="run_cmd",
    args_schema=RunCmdInput,
    description="Run a shell command safely inside the project directory."
)
