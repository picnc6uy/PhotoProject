# OpenAI Agent Design and Best Practices

_Imported: 2026-02-10 (from local reference "Open AI agent Design Best Practices.md")_

## Purpose
Summarizes practical best practices for designing OpenAI-powered agent systems where Python handles orchestration, state, cost, schemas, retrieval, scoring, and permissions. Emphasizes disciplined agent roles over loosely connected swarms.

## Key Principles
1. **Agents as contractual roles**
   - Define purpose, inputs, outputs, forbidden behavior, and schemas for each agent role (e.g., Claim Extractor, Evidence Assessor).
2. **Central orchestrator**
   - Python decides which model, tools, and workflows to execute. LLMs handle judgment-heavy language tasks.
3. **Minimize model calls**
   - Use batch operations; aim for quick (≈3 calls), standard (≈5–8), deep audit (as needed) modes.
4. **Structured outputs**
   - Enforce JSON schema validation (e.g., Claim, EvidencePack, ScoreCard) for all LLM responses before advancing pipeline stages.
5. **Tool discipline**
   - Register narrow, typed tools (search_vetted_sources, retrieve_passages, calculate_score). Log usage and prevent agents from inventing tools.
6. **Retrieval-first truth model**
   - Treat vetted sources as the ground truth; the LLM judges evidence vs. claim rather than relying on its own memory.
7. **Source registry**
   - Maintain YAML (authority level, allowed domains) to constrain retrieval.
8. **Cost controls**
   - Cap claims per run, sources per claim, model calls per mode, and reuse cached intermediate outputs.
9. **Escalation gates**
   - Only trigger expensive reviews (red team, specialists) when confidence is low or impact high.
10. **Agent contracts**
    - Document purpose, inputs, outputs, and rules for each agent.
11. **Guardrails & safety**
    - Validate outputs, enforce citations, block prompt injection, restrict tool access, and log everything.
12. **Handoffs**
    - Introduce specialized agent delegation only after stabilizing the core orchestrator.
13. **Tracing & observability**
    - Persist run artifacts (e.g., `reports/run_001/claims.json`, `run_log.json`) to debug failures.
14. **Evaluation strategy**
    - Maintain a labeled test set of claims; evaluate extraction, retrieval, assessment, logic, and reporting separately.
15. **Python stack**
    - Start with Python 3.12, Pydantic, pytest, OpenAI API, vector store; expand to FastAPI/Streamlit/etc. later.
16. **VS Code & Continue workflow**
    - Give the assistant precise instructions; enforce project rules for edits, tests, and documentation.
17. **Recommended file structure**
    - Organize orchestrator, schemas, pipeline stages, tools, data, reports, and tests.
18. **Model selection**
    - Reserve powerful models for nuanced reasoning; use cheaper models or pure Python for rote tasks.
19. **Failure modes**
    - Guard against over/under extraction, irrelevant evidence, overconfidence, prompt injection, and cost blow-ups via schemas and evaluation.
20. **Scoring philosophy**
    - Use multi-dimensional scoring (Evidence Match, Source Quality, Specificity, etc.) rather than a single truth metric.
21. **MVP workflow**
    - Start simple: local transcripts → top claims → local vetted sources → assessments → Markdown report.
22. **Build sequence**
    - Establish contracts, schemas, CLI, extraction, registry, retrieval, assessment, scoring, reporting, and evals before advanced integrations.
23. **Operating rule**
    - “LLM reads, extracts, compares, and explains; Python controls, validates, scores, logs, and limits; vetted sources are the authority; evals are the judge.”

## Action Items for Our Platform
- Align agent contracts with this blueprint when defining future roles.
- Incorporate cost controls and escalation gates in our orchestration plans.
- Use this document to seed ADRs for orchestration style, tool access policies, and evaluation strategy.
