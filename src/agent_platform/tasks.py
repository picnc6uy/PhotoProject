"""Task specifications and helper utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AcceptanceCriteria:
    """Represents objective conditions that define task success."""

    description: str
    automated_checks: List[str] = field(default_factory=list)
    manual_notes: List[str] = field(default_factory=list)


@dataclass
class TaskSpec:
    """Structured description of a software development task."""

    title: str
    summary: str
    requirements: List[str] = field(default_factory=list)
    acceptance: List[AcceptanceCriteria] = field(default_factory=list)
    repo_hint: Optional[str] = None
    entry_point: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_prompt(self) -> str:
        """Create a natural-language prompt for language-model reasoning."""
        lines = [f"Task: {self.title}", "", self.summary, ""]
        if self.requirements:
            lines.append("Requirements:")
            lines.extend(f"- {req}" for req in self.requirements)
            lines.append("")
        if self.acceptance:
            lines.append("Acceptance Criteria:")
            for criterion in self.acceptance:
                lines.append(f"- {criterion.description}")
                for check in criterion.automated_checks:
                    lines.append(f"  * Auto-check: {check}")
                for note in criterion.manual_notes:
                    lines.append(f"  * Manual: {note}")
            lines.append("")
        if self.repo_hint:
            lines.append(f"Repository hint: {self.repo_hint}")
        if self.entry_point:
            lines.append(f"Suggested entry point: {self.entry_point}")
        if self.metadata:
            lines.append("Metadata:")
            lines.extend(f"- {key}: {value}" for key, value in self.metadata.items())
        return "\n".join(lines)
