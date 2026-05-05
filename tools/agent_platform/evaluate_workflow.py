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
from agent_platform.tools import EditorTool, GitTool, ShellCommandTool, ToolRegistry

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
    registry.register(
        ShellCommandTool(
            working_dir=str(workspace),
            allowed_prefixes=["echo", "pytest", "flake8", "git status", "git add"],
        )
    )
    registry.register(GitTool(working_dir=str(workspace), allowed_commands=["status", "diff", "add"]))
    registry.register(EditorTool(root=str(workspace)))
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


def summarize_results(records: dict) -> dict:
    summary = {}

    test_agent = records.get("TestRunnerAgent", {})
    test_summary = test_agent.get("state", {}).get("artifacts", {}).get("test_run", {}).get("summary", {})
    summary["tests"] = {
        "passed": test_summary.get("passed", 0),
        "failed": test_summary.get("failed", 0),
        "skipped": test_summary.get("skipped", 0),
    }

    verification = records.get("RequirementsVerifier", {})
    verification_summary = (
        verification.get("state", {})
        .get("artifacts", {})
        .get("verification", {})
        .get("summary", {})
    )
    summary["requirements"] = {
        "satisfied": verification_summary.get("satisfied", 0),
        "unsatisfied": verification_summary.get("unsatisfied", 0),
    }

    red_team = records.get("RedTeamReviewer", {})
    verdict = (
        red_team.get("state", {})
        .get("artifacts", {})
        .get("red_team", {})
        .get("verdict", "unknown")
    )
    summary["red_team_verdict"] = verdict

    review = records.get("CodeReviewer", {})
    decision = (
        review.get("state", {})
        .get("artifacts", {})
        .get("review", {})
        .get("decision", "pending")
    )
    summary["review_decision"] = decision

    return summary


def save_results(records: dict, summary: dict, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    payload = {"agents": records, "summary": summary}
    path = directory / f"evaluation_{timestamp}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the agent workflow evaluation harness")
    parser.add_argument("--workspace", default=".", help="Workspace directory for tool execution")
    parser.add_argument("--task", type=Path, default=DEFAULT_TASK, help="Path to YAML task file")
    parser.add_argument("--allow-shell", nargs="*", help="Additional shell command prefixes to allow")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    task = load_task(Path(args.task))
    registry = build_registry(workspace)
    if args.allow_shell:
        shell_tool = registry.get("shell")
        if shell_tool and hasattr(shell_tool, "allowed_prefixes"):
            shell_tool.allowed_prefixes.extend(args.allow_shell)

    records = run_evaluation(task, registry)
    summary = summarize_results(records)
    output = save_results(records, summary, EVAL_DIR)

    print(f"Evaluation saved to {output}")
    print("Summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
