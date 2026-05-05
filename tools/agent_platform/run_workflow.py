"""Simple CLI helper to run the agent workflow via the Orchestrator."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    yaml = None

from agent_platform import (
    AgentArchitect,
    AgentConfig,
    DesignAdvisor,
    ImplementerAgent,
    IntegratorAgent,
    PlannerAgent,
    PostMergeObserver,
    ReleaseCoordinator,
    ResourceSurveyor,
    RequirementsVerifier,
    RiskMonitor,
    TaskRefiner,
    TaskSpec,
    TestRunnerAgent,
)
from agent_platform.agents import CodeReviewer, RedTeamReviewer
from agent_platform.orchestrator import Orchestrator
from agent_platform.tools import ShellCommandTool, ToolRegistry


def build_registry(workspace: Path) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ShellCommandTool(working_dir=str(workspace)))
    return registry


def _from_yaml(task_file: Path) -> TaskSpec:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load YAML task files.")
    data: Dict[str, Any] = yaml.safe_load(task_file.read_text(encoding="utf-8")) or {}
    return TaskSpec(
        title=data.get("title", task_file.stem),
        summary=data.get("summary", ""),
        requirements=data.get("requirements", []),
        acceptance=data.get("acceptance", []),
        metadata=data.get("metadata", {}),
    )


def make_task(task_file: Path | None) -> TaskSpec:
    if task_file and task_file.exists():
        if task_file.suffix.lower() in {".yml", ".yaml"}:
            return _from_yaml(task_file)
        data = task_file.read_text(encoding="utf-8")
        return TaskSpec(title=task_file.stem, summary=data[:200], requirements=[data])
    return TaskSpec(
        title="Agent workflow dry run",
        summary="Execute orchestrator workflow to verify agent readiness.",
        requirements=["Survey resources", "Refine requirements", "Plan work"],
        metadata={
            "touches_docs": True,
            "test_commands": ["echo pytest -q"],
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the agent orchestrator workflow")
    parser.add_argument("--workspace", default=".", help="Workspace directory for tool execution")
    parser.add_argument("--task-file", type=Path, help="Optional file describing the task")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    registry = build_registry(workspace)
    orchestrator = Orchestrator(registry)

    task = make_task(args.task_file)
    agent_sequence = [
        ResourceSurveyor,
        TaskRefiner,
        RiskMonitor,
        PlannerAgent,
        DesignAdvisor,
        ImplementerAgent,
        TestRunnerAgent,
        CodeReviewer,
        RequirementsVerifier,
        RedTeamReviewer,
        IntegratorAgent,
        ReleaseCoordinator,
        PostMergeObserver,
        AgentArchitect,
    ]

    records = orchestrator.run_workflow(agent_sequence, task)
    for name, record in records.items():
        outcome = record["state"].get("outcome")
        print(f"{name}: {outcome}")


if __name__ == "__main__":
    main()
