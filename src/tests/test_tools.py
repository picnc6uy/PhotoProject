from __future__ import annotations

from agent_platform.tools import ShellCommandTool, ToolContext


def test_shell_command_tool_allows_configured_commands(tmp_path):
    tool = ShellCommandTool(working_dir=str(tmp_path), allowed_prefixes=["echo"])
    output = tool.run("echo hello", ToolContext(working_dir=str(tmp_path)))
    assert "hello" in output


def test_shell_command_tool_blocks_unlisted_commands(tmp_path):
    tool = ShellCommandTool(working_dir=str(tmp_path), allowed_prefixes=["echo"])
    output = tool.run("npm install", ToolContext(working_dir=str(tmp_path)))
    assert "not permitted" in output
