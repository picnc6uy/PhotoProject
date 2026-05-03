"""Orchestration utilities for coordinating agent runs with caching."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .agents import Agent
from .tasks import TaskSpec
from .tools import ToolRegistry


@dataclass
class OrchestratorRecord:
    """Serializable record of an agent run."""

    agent_name: str
    task: Dict[str, Any]
    state: Dict[str, Any]
    config: Dict[str, Any]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": {
                "name": self.agent_name,
                "config": self.config,
            },
            "task": self.task,
            "state": self.state,
            "metadata": self.metadata,
        }


class CacheStore:
    """Simple JSON-based cache for agent run artefacts."""

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def make_key(self, agent_name: str, task: TaskSpec) -> str:
        payload = {
            "agent": agent_name,
            "task": asdict(task),
        }
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def load(self, key: str) -> Optional[Dict[str, Any]]:
        path = self.root / f"{key}.json"
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def save(self, key: str, record: OrchestratorRecord) -> None:
        path = self.root / f"{key}.json"
        with path.open("w", encoding="utf-8") as fh:
            json.dump(record.to_dict(), fh, indent=2, sort_keys=True)


class Orchestrator:
    """Coordinates agent execution with optional caching."""

    def __init__(
        self,
        tools: ToolRegistry,
        cache_dir: Path | str = Path("dev_data/agent_platform/cache"),
    ):
        self.tools = tools
        self.cache = CacheStore(Path(cache_dir))

    def run(
        self,
        agent: Agent,
        task: TaskSpec,
        *,
        use_cache: bool = True,
    ) -> Tuple[Dict[str, Any], bool]:
        """Execute the agent on the task, returning (record, from_cache)."""

        cache_key = self.cache.make_key(agent.config.name, task)
        if use_cache:
            cached = self.cache.load(cache_key)
            if cached is not None:
                return cached, True

        state = agent.run(task)
        record = self._build_record(agent, task, state, cache_key)
        if use_cache:
            self.cache.save(cache_key, record)
        return record.to_dict(), False

    def _build_record(
        self,
        agent: Agent,
        task: TaskSpec,
        state,
        cache_key: str,
    ) -> OrchestratorRecord:
        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
        state_dict = _state_to_dict(state)
        tools = [f"{tool.name}: {tool.description}" for tool in self.tools.list_tools()]
        metadata = {
            "cache_key": cache_key,
            "created_at": timestamp,
            "tools": tools,
            "iterations": state_dict.get("iteration"),
        }
        config_summary = {
            "max_iterations": agent.config.max_iterations,
            "description": agent.config.description,
            "metadata": agent.config.metadata,
        }
        return OrchestratorRecord(
            agent_name=agent.config.name,
            task=asdict(task),
            state=state_dict,
            config=config_summary,
            metadata=metadata,
        )


def _state_to_dict(state) -> Dict[str, Any]:
    """Convert AgentState to a serializable dict."""
    if hasattr(state, "__dict__"):
        base = {
            "iteration": state.iteration,
            "plan": list(state.plan),
            "actions": list(state.actions),
            "artifacts": state.artifacts,
            "notes": list(state.notes),
            "outcome": state.outcome,
        }
        return base
    raise TypeError("Unsupported state object for serialization")
