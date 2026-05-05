# Safety and Security Considerations for Agent Workflows

_Last updated: 2026-02-10_

## Principles
- **Least privilege**: Grant agents only the tool permissions they need (e.g., read-only git, sandboxed shell, no network by default).
- **Human-in-the-loop**: Require explicit confirmation for high-impact actions (deployments, mass refactors, dependency upgrades).
- **Observability**: Log every tool invocation, argument, and result. Store logs with timestamps and agent identifiers.

## Sensitive Data Handling
- **Secrets**: Never hardcode API keys or credentials. Routes should source environment variables or secret managers outside the repo.
- **Sanitization**: Strip sensitive paths or tokens from agent output before persisting or displaying to untrusted channels.
- **Data retention**: Define retention policies for logs, artifacts, and generated code to comply with organizational guidelines.

## Tool Security
- **Shell commands**: Enforce allowlists, run in sandboxed directories, and monitor for long-running processes. Provide safe cancellation mechanisms.
- **Network access**: Gate all outbound requests; log target domains and responses for audit.
- **File edits**: Use staging areas or diff previews before writing changes to disk. Validate file paths to avoid directory traversal.

## Failure Handling
- **Retry with backoff**: For transient errors (rate limits, network hiccups), retry safely with capped attempts.
- **Fallback strategies**: If a tool fails or is unavailable, agents should surface the issue with context and alternate suggestions.
- **Abort conditions**: Define thresholds (e.g., repeated test failures, unexpected deletions) that trigger immediate stop and human review.

## Documentation & Governance
- **Architecture Decision Records (ADRs)**: Record major security-related decisions and rationale.
- **Playbooks**: Maintain incident response steps if an agent behaves unexpectedly.
- **Training & onboarding**: Ensure contributors understand the agent safety model before extending capabilities.

Refer to this guide when designing new agents or expanding tool access. Update it as policies evolve.
