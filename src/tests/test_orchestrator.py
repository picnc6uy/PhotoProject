from __future__ import annotations

from typing import Dict

from agent_platform.agents import AgentConfig
from agent_platform.agents.base import Agent
from agent_platform.orchestrator import Orchestrator
from agent_platform.tasks import TaskSpec
from agent_platform.tools import ToolRegistry


class DeterministicAgent(Agent):
    """Agent that records deterministic actions for testing the orchestrator."""

    def __init__(self, config: AgentConfig, tools: ToolRegistry):
        super().__init__(config, tools)

    def plan(self, task: TaskSpec):  # type: ignore[override]
        return ["inspect task", "produce guidance"]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        return state.iteration > len(state.plan)

    def act(self, task: TaskSpec, state) -> Dict[str, str]:  # type: ignore[override]
        index = state.iteration - 1
        step = state.plan[index]
        return {"step": step, "detail": f"{step} for {task.title}"}

    def observe(self, task: TaskSpec, state, action):  # type: ignore[override]
        return f"Executed {action['step']}"

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        return f"Completed {task.title}"


def test_orchestrator_caches_agent_runs(tmp_path):
    registry = ToolRegistry()
    config = AgentConfig(name="deterministic", max_iterations=5)
    agent = DeterministicAgent(config, registry)
    orchestrator = Orchestrator(registry, cache_dir=tmp_path)

    task = TaskSpec(title="Test orchestration", summary="", requirements=["R1"])

    record, from_cache = orchestrator.run(agent, task, use_cache=True)
    assert not from_cache
    assert record["state"]["actions"]  # actions captured

    cached_record, from_cache = orchestrator.run(agent, task, use_cache=True)
    assert from_cache
    assert cached_record == record


def test_orchestrator_bypass_cache(tmp_path):
    registry = ToolRegistry()
    config = AgentConfig(name="deterministic", max_iterations=5)
    agent = DeterministicAgent(config, registry)
    orchestrator = Orchestrator(registry, cache_dir=tmp_path)

    task = TaskSpec(title="Test orchestration", summary="", requirements=["R1"])

    record, from_cache = orchestrator.run(agent, task, use_cache=True)
    assert not from_cache

    second_record, from_cache = orchestrator.run(agent, task, use_cache=False)
    assert not from_cache
    assert second_record["metadata"]["created_at"] >= record["metadata"]["created_at"]
