# OpenAI Agent Design – Distilled Takeaways

_Last updated: 2026-02-10_

## Core Philosophy
- Treat the agent system as a **controlled pipeline** driven by Python orchestration; use LLM calls only for judgment-heavy language tasks.
- Define each agent as a **contracted role** with clear responsibilities, inputs, outputs, and forbidden behaviours.

## Architecture Snapshot
1. **Ingest** user input → preprocess in Python.
2. **LLM (batch) extraction/classification** of claims or tasks.
3. **Python orchestration** for deduplication, retrieval, routing, and scoring.
4. **LLM assessment** against vetted evidence packs.
5. **Python logic checks & scoring** with escalation gates.
6. **LLM final reporting** only when needed.
7. **Python export** of structured outputs + human-readable report.

## Design Rules (TL;DR)
- **Few model calls**: quick ≈3, standard ≈5–8, deep audit only when required.
- **Structured output**: enforce JSON schema (Pydantic) validation between stages.
- **Retrieval-first**: the LLM compares claims to vetted sources; it is never treated as the source of truth.
- **Tool discipline**: register narrow, typed tools; log usage; prohibit ad-hoc tool creation.
- **Cost gates**: cap claims, sources, and model invocations; cache intermediate work.
- **Escalation gates**: only invoke red-team or specialist passes when confidence is low or risk is high.
- **Guardrails**: block unsupported sources, enforce citations, sanitize outputs, prevent prompt injection.
- **Observability**: log prompts, tool calls, evidence, outputs, and validation errors per run.
- **Evaluation-first**: maintain a labeled test set exercising extraction, retrieval, assessment, logic, and reporting dimensions.

## Recommended Build Sequence (Key Milestones)
1. Establish system contract + Pydantic schemas.
2. Build orchestrator CLI skeleton.
3. Implement claim/task extraction with structured output.
4. Stand up vetted-source registry & retrieval.
5. Build evidence assessment + scoring.
6. Produce report writer + JSON artifacts.
7. Add regression evals.
8. Layer in advanced ingestion, dashboards, and optional OpenAI Agents SDK.

## Practical Commandments
- “LLM reads/explains; Python controls/validates/logs; vetted sources rule; evals judge.”
- Keep VS Code assistants constrained: precise instructions, small diffs, tests before commits.
- Never store secrets in code; wrap risky operations with human checkpoints.

Refer back to `openai_agent_design_best_practices.md` for the full blueprint when more nuance or examples are needed.
