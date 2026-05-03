from __future__ import annotations

from typing import Dict

from agent_platform.agents import AgentArchitect, AgentConfig
from agent_platform.agents.base import Agent
from agent_platform.tasks import AcceptanceCriteria, TaskSpec
from agent_platform.tools import Tool, ToolContext, ToolRegistry


class EchoTool(Tool):
    def __init__(self):
        super().__init__(name="echo", description="Echo command for testing")

    def run(self, command: str, context: ToolContext) -> str:
        return f"ECHO:{command}@{context.working_dir}"


class DummyAgent(Agent):
    def __init__(self, config: AgentConfig, tools: ToolRegistry):
        super().__init__(config, tools)
        self._step_index = 0

    def reset(self) -> None:
        super().reset()
        self._step_index = 0

    def plan(self, task: TaskSpec):
        return ["review requirements", "implement solution", "run tests"]

    def should_stop(self, task: TaskSpec, state):  # type: ignore[override]
        # Stop after completing planned steps or reaching the default max.
        return state.iteration > len(state.plan) or super().should_stop(task, state)

    def act(self, task: TaskSpec, state) -> Dict[str, str]:  # type: ignore[override]
        tool = self.tools.get("echo")
        assert tool is not None
        plan_step = state.plan[min(self._step_index, len(state.plan) - 1)]
        command = f"{plan_step} for {task.title}"
        self._step_index += 1
        output = tool.run(command, ToolContext(working_dir="/workspace"))
        return {"command": command, "output": output}

    def observe(self, task: TaskSpec, state, action):  # type: ignore[override]
        return f"Observed output: {action['output']}"

    def summarize(self, task: TaskSpec, state) -> str:  # type: ignore[override]
        return f"Completed {task.title} in {len(state.actions)} steps"


def test_tool_registry_register_and_describe():
    registry = ToolRegistry()
    echo = EchoTool()
    registry.register(echo)

    assert registry.get("echo") is echo
    description = registry.describe()
    assert "echo" in description
    assert "Available tools" in description


def test_task_spec_to_prompt_includes_acceptance():
    task = TaskSpec(
        title="Add feature flag",
        summary="Introduce a feature flag to toggle the new workflow.",
        requirements=["Feature flag default OFF", "Configurable via environment"],
        acceptance=[
            AcceptanceCriteria(
                description="Existing tests continue to pass",
                automated_checks=["pytest -q"],
                manual_notes=["Product sign-off"]
            )
        ],
        repo_hint="app/feature_flags.py",
        entry_point="src/app/main.py",
        metadata={"priority": "high"},
    )

    prompt = task.to_prompt()
    assert "Acceptance Criteria" in prompt
    assert "Auto-check: pytest -q" in prompt
    assert "Manual: Product sign-off" in prompt
    assert "priority: high" in prompt


def test_dummy_agent_runs_plan(monkeypatch):
    registry = ToolRegistry()
    registry.register(EchoTool())
    config = AgentConfig(name="dummy", max_iterations=5)
    agent = DummyAgent(config, registry)

    task = TaskSpec(title="Refactor module", summary="", requirements=[])

    state = agent.run(task)

    assert state.outcome == "Completed Refactor module in 3 steps"
    assert len(state.actions) == 3
    assert state.iteration >= len(state.actions)
    assert all("ECHO:" in action["output"] for action in state.actions)


def test_agent_architect_produces_workspace_specific_plan():
    registry = ToolRegistry()
    registry.register(EchoTool())
    config = AgentConfig(name="architect", max_iterations=10)
    agent = AgentArchitect(config, registry)

    task = TaskSpec(
        title="Bootstrap expert agent guidance",
        summary="Create advisory plan for building agents tailored to this workspace.",
        requirements=[
            "Leverage existing documentation",
            "Consider available tools and tests",
            "Outline validation strategy",
        ],
        metadata={
            "workspace_docs": [
                "MASTER_PROJECT_CONTEXT.md",
                "docs/agents/PROJECT_CHARTER.md",
            ],
            "available_tools": ["shell: execute controlled shell commands"],
            "test_commands": ["pytest -q"],
            "focus_area": "agent bootstrap",
        },
    )

    state = agent.run(task)

    assert state.outcome.startswith("Architected plan for 'Bootstrap expert agent guidance'")
    assert len(state.actions) == len(state.plan)
    assert state.artifacts["architecture_notes"]  # notes recorded for each step
    first_action = state.actions[0]
    assert "workspace_docs" in first_action["environment"]
    assert any("focus area" in note for note in state.artifacts["architecture_notes"][0]["recommendations"])
