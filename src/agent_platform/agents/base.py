"""Abstract base classes and shared utilities for software developer agents."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from ..tasks import TaskSpec
from ..tools import ToolRegistry


@dataclass
class AgentConfig:
    """Configuration bundle for an agent instance."""

    name: str
    description: str = ""
    max_iterations: int = 50
    allow_network: bool = False
    allow_shell: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Mutable state tracked across the agent reasoning loop."""

    iteration: int = 0
    plan: List[str] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    outcome: Optional[str] = None


class Agent(abc.ABC):
    """Base class for all software developer agents."""

    def __init__(self, config: AgentConfig, tools: ToolRegistry):
        self.config = config
        self.tools = tools
        self.state = AgentState()

    def reset(self) -> None:
        """Reset the agent state before starting a new task."""
        self.state = AgentState()

    def run(self, task: TaskSpec) -> AgentState:
        """Execute the agent loop on the provided task."""
        self.reset()
        self.state.plan = list(self.plan(task))
        for self.state.iteration in range(1, self.config.max_iterations + 1):
            if self.should_stop(task, self.state):
                break
            action = self.act(task, self.state)
            self.state.actions.append(action)
            observation = self.observe(task, self.state, action)
            self.state.notes.append(observation)
            self.after_iteration(task, self.state, action, observation)
        self.state.outcome = self.summarize(task, self.state)
        return self.state

    @abc.abstractmethod
    def plan(self, task: TaskSpec) -> Iterable[str]:
        """Generate an initial high-level plan for the task."""

    @abc.abstractmethod
    def act(self, task: TaskSpec, state: AgentState) -> Dict[str, Any]:
        """Produce the next action given the current state."""

    @abc.abstractmethod
    def observe(self, task: TaskSpec, state: AgentState, action: Dict[str, Any]) -> str:
        """Generate an observation/analysis string after an action executes."""

    @abc.abstractmethod
    def summarize(self, task: TaskSpec, state: AgentState) -> str:
        """Return the final outcome summary for the completed task."""

    def should_stop(self, task: TaskSpec, state: AgentState) -> bool:
        """Hook to determine whether the agent should stop iterating."""
        return state.iteration >= self.config.max_iterations

    def after_iteration(
        self,
        task: TaskSpec,
        state: AgentState,
        action: Dict[str, Any],
        observation: str,
    ) -> None:
        """Optional hook called after each iteration for bookkeeping."""
        # Default implementation does nothing; subclasses may override.
        return None
