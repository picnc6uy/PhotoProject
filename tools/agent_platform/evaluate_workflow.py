"""Evaluation harness for the agent workflow."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, UTC
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

from agent_platform import (
    AgentArchitect,
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

DEFAULT_TASK = Path("dev_data/agent_platform/tasks/sample_task.yaml")
EVAL_DIR = Path("dev_data/agent_platform/evaluations")


def load_task(path: Path) -> TaskSpec:
    if not path.exists():
        raise FileNotFoundError(f"Task file not found: {path}")
    if path.suffix.lower() in {".yml", ".yaml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required to load YAML evaluation tasks.")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return TaskSpec(
            title=data.get("title", path.stem),
            summary=data.get("summary", ""),
            requirements=data.get("requirements", []),
            acceptance=data.get("acceptance", []),
            metadata=data.get("metadata", {}),
        )
    text = path.read_text(encoding="utf-8")
    return TaskSpec(title=path.stem, summary=text[:200], requirements=[text])


def build_registry(workspace: Path) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ShellCommandTool(working_dir=str(workspace)))
    return registry


def run_evaluation(task: TaskSpec, registry: ToolRegistry) -> dict:
    orchestrator = Orchestrator(registry)
    agents = [
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
    return orchestrator.run_workflow(agents, task)


def save_results(results: dict, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"evaluation_{timestamp}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, sort_keys=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the agent workflow evaluation harness")
    parser.add_argument("--workspace", default=".", help="Workspace directory for tool execution")
    parser.add_argument("--task", type=Path, default=DEFAULT_TASK, help="Path to YAML task file")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    task = load_task(Path(args.task))
    registry = build_registry(workspace)

    results = run_evaluation(task, registry)
    output = save_results(results, EVAL_DIR)
    print(f"Evaluation saved to {output}")


if __name__ == "__main__":
    main()
