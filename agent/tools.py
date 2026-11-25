"""Sandboxed file helpers: generated code can only be written inside the project folder."""
import pathlib

PROJECT_ROOT: pathlib.Path | None = None


def set_project_root(root: pathlib.Path) -> None:
    """Set the folder that all generated files must stay inside."""
    global PROJECT_ROOT
    PROJECT_ROOT = pathlib.Path(root)


def safe_path_for_project(path: str) -> pathlib.Path:
    """Resolve `path` inside PROJECT_ROOT, refusing anything that escapes it."""
    if PROJECT_ROOT is None:
        raise RuntimeError("PROJECT_ROOT not initialized - call set_project_root() first.")
    root = PROJECT_ROOT.resolve()
    candidate = pathlib.Path(path)
    if candidate.is_absolute():
        raise ValueError(f"Absolute paths are not allowed: {path}")
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Attempt to access path outside project root: {path}")
    return resolved


def write_file(path: str, content: str) -> str:
    """Write a file inside the project folder and return its relative path."""
    p = safe_path_for_project(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return str(p.relative_to(PROJECT_ROOT.resolve()))


def read_file(path: str) -> str:
    """Read a file inside the project folder ('' if it does not exist)."""
    p = safe_path_for_project(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def list_files() -> list[str]:
    """List all files in the project folder, relative to it."""
    if PROJECT_ROOT is None:
        return []
    root = PROJECT_ROOT.resolve()
    return sorted(str(f.relative_to(root)) for f in root.rglob("*") if f.is_file())
