"""Tool abstractions and registries for agent actions."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Dict, Iterable, Optional


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
