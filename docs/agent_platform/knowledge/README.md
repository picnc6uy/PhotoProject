# Agent Knowledge Base

This directory centralizes reference material that AgentArchitect and other agents should consult before planning or implementing work.

## How to contribute
1. **Add source summaries**
   - Create a new Markdown file per topic: e.g., `openai_assistants_overview.md`, `safe_tool_usage.md`.
   - Include a short abstract, key takeaways, and links or citations to the original material.
   - Note the retrieval date and method (manual import, API fetch, etc.).
2. **Update existing summaries**
   - Append a dated changelog section for major revisions.
   - Preserve prior context unless it has been superseded.
3. **Record fetch limitations**
   - If a resource was inaccessible (e.g., HTTP 403), note it so we can retry later.
4. **Keep it actionable**
   - Highlight how the information impacts agent design, safety, or evaluation.

## Suggested topics
- OpenAI Assistants / function-calling capabilities
- Agent orchestration patterns and planning loops
- Safety, security, and compliance guidelines
- Evaluation harness design and benchmarking practices
- Tooling adapters (shell, git, editor, test runners)

## Current contents (Feb 10, 2026)
- `openai_assistants_overview.md` (placeholder; document fetch pending)
- `openai_agent_design_best_practices.md` (full reference import)
- `openai_agent_design_distilled.md` (quick-reference summary)
- `agent_orchestration_best_practices.md`
- `safety_and_security.md`

Agents should read relevant summaries during their planning phase and cite them in their `architecture_notes` artifacts for traceability.
