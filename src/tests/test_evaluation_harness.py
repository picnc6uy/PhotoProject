from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from agent_platform.tasks import TaskSpec
from agent_platform.tools import ToolRegistry, ShellCommandTool
from tools.agent_platform.evaluate_workflow import run_evaluation, save_results, summarize_results


def test_evaluation_harness_saves_results(tmp_path):
    registry = ToolRegistry()
    registry.register(ShellCommandTool(working_dir=str(tmp_path)))
    task = TaskSpec(
        title="Eval harness test",
        summary="",
        requirements=["Test run"],
        metadata={"test_commands": ["echo pytest -q"]},
    )

    records = run_evaluation(task, registry)
    summary = summarize_results(records)
    out_path = save_results(records, summary, tmp_path)

    assert out_path.exists()
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert "ResourceSurveyor" in data["agents"]
    assert "tests" in data["summary"]
