"""Tool abstractions and registries for agent actions."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
import subprocess


@dataclass
class ToolContext:
    """Context provided to tool executions."""

    working_dir: str
    allow_network: bool = False
    allow_filesystem: bool = True


class Tool(abc.ABC):
    """Interface for callable tools that agents may invoke."""

    name: str
    description: str

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abc.abstractmethod
    def run(self, command: str, context: ToolContext) -> str:
        """Execute the tool with the provided command and context."""

    def run_batch(self, commands: List[str], context: ToolContext) -> List[str]:
        """Execute multiple commands, defaulting to sequential execution."""
        return [self.run(command, context) for command in commands]


class ToolRegistry:
    """Registry of tools available to an agent."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> Iterable[Tool]:
        return self._tools.values()

    def describe(self) -> str:
        lines = ["Available tools:"]
        for tool in self._tools.values():
            lines.append(f"- {tool.name}: {tool.description}")
        return "\n".join(lines)


class ShellCommandTool(Tool):
    """Executes shell commands with optional batching support."""

    DEFAULT_ALLOWED_PREFIXES = ["echo", "pytest", "flake8", "git status", "git add"]

    def __init__(
        self,
        working_dir: str | None = None,
        allow_network: bool = False,
        allowed_prefixes: Optional[List[str]] = None,
    ):
        super().__init__(name="shell", description="Execute shell commands in the workspace")
        self.default_working_dir = working_dir or "."
        self.allow_network = allow_network
        self.allowed_prefixes = allowed_prefixes or list(self.DEFAULT_ALLOWED_PREFIXES)

    def run(self, command: str, context: ToolContext) -> str:  # type: ignore[override]
        return self._execute(command, context)

    def run_batch(self, commands: List[str], context: ToolContext) -> List[str]:  # type: ignore[override]
        return [self._execute(command, context) for command in commands]

    def _allowed(self, command: str) -> bool:
        stripped = command.lstrip()
        return any(stripped.startswith(prefix) for prefix in self.allowed_prefixes)

    def _execute(self, command: str, context: ToolContext) -> str:
        if not self._allowed(command):
            return f"Command '{command}' is not permitted by shell allow-list."

        working_dir = context.working_dir or self.default_working_dir
        completed = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
        )
        output = completed.stdout.strip()
        if completed.stderr:
            output = f"{output}\n{completed.stderr.strip()}" if output else completed.stderr.strip()
        if completed.returncode != 0 and not output:
            output = f"Command exited with status {completed.returncode}"
        return output
