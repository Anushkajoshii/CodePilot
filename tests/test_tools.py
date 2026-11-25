import pytest

from agent import tools


def test_sandbox_blocks_escape(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    tools.set_project_root(root)
    assert tools.write_file("src/a.js", "1") == "src/a.js"
    with pytest.raises(ValueError):
        tools.safe_path_for_project("../evil.txt")
    with pytest.raises(ValueError):
        tools.safe_path_for_project("/etc/passwd")
    # a sibling folder whose name starts with the root's name must also be refused
    (tmp_path / "proj_evil").mkdir()
    with pytest.raises(ValueError):
        tools.safe_path_for_project("../proj_evil/x")
