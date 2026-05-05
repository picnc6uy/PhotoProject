from __future__ import annotations

from agent_platform.agents import AgentConfig, RedTeamReviewer
from agent_platform.tasks import TaskSpec
from agent_platform.tools import ToolRegistry


def make_task(metadata=None):
    return TaskSpec(
        title="Assess workflow rigor",
        summary="Red-team the proposed plan and evidence.",
        requirements=["Verify risk mitigation", "Confirm tests run"],
        metadata=metadata or {},
    )


def test_red_team_flags_missing_evidence():
    registry = ToolRegistry()
    agent = RedTeamReviewer(AgentConfig(name="red_team", max_iterations=5), registry)

    task = make_task(
        metadata={
            "requires_rollback_plan": True,
            "review_decision": "changes_requested",
            "test_results": None,
        }
    )
    state = agent.run(task)

    findings = state.artifacts["red_team"]
    assert any("rollback" in gap.lower() for gap in findings["gaps"])
    assert findings["verdict"] == "reject"


def test_red_team_accepts_when_evidence_strong():
    registry = ToolRegistry()
    agent = RedTeamReviewer(AgentConfig(name="red_team", max_iterations=5), registry)

    task = make_task(
        metadata={
            "requires_rollback_plan": False,
            "review_decision": "approved",
            "test_results": [{"command": "echo tests", "status": "passed"}],
        }
    )
    state = agent.run(task)

    verdict = state.artifacts["red_team"]["verdict"]
    assert verdict in {"accept", "escalate"}
