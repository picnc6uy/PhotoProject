from __future__ import annotations

import subprocess

from agent_platform.tools import EditorTool, GitTool, ShellCommandTool, ToolContext


def test_shell_command_tool_allows_configured_commands(tmp_path):
    tool = ShellCommandTool(working_dir=str(tmp_path), allowed_prefixes=["echo"])
    output = tool.run("echo hello", ToolContext(working_dir=str(tmp_path)))
    assert "hello" in output


def test_shell_command_tool_blocks_unlisted_commands(tmp_path):
    tool = ShellCommandTool(working_dir=str(tmp_path), allowed_prefixes=["echo"])
    output = tool.run("npm install", ToolContext(working_dir=str(tmp_path)))
    assert "not permitted" in output


def test_git_tool_allows_status(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "example.txt").write_text("data", encoding="utf-8")
    tool = GitTool(working_dir=str(tmp_path), allowed_commands=["status"])
    output = tool.run("status --short", ToolContext(working_dir=str(tmp_path)))
    assert "?? example.txt" in output


def test_git_tool_blocks_disallowed_command(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    tool = GitTool(working_dir=str(tmp_path), allowed_commands=["status"])
    output = tool.run("commit -m test", ToolContext(working_dir=str(tmp_path)))
    assert "not permitted" in output


def test_editor_tool_read_preview(tmp_path):
    file_path = tmp_path / "note.txt"
    file_path.write_text("line1\nline2", encoding="utf-8")
    tool = EditorTool(root=str(tmp_path))
    read_output = tool.run("read note.txt", ToolContext(working_dir=str(tmp_path)))
    assert "line1" in read_output
    preview = tool.run("preview note.txt", ToolContext(working_dir=str(tmp_path)))
    assert "line1" in preview


def test_editor_tool_write_requires_permission(tmp_path):
    tool = EditorTool(root=str(tmp_path), allow_write=False)
    denied = tool.run("write note.txt::content", ToolContext(working_dir=str(tmp_path)))
    assert "not permitted" in denied

    writable = EditorTool(root=str(tmp_path), allow_write=True)
    success = writable.run("write note.txt::content", ToolContext(working_dir=str(tmp_path)))
    assert "Wrote" in success
    assert (tmp_path / "note.txt").read_text(encoding="utf-8") == "content"
