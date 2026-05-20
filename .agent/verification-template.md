---
task-id: T-XXX
verified: YYYY-MM-DD
status: draft
agent: claude-code
---

# Verification for T-XXX

## Automated checks
- [ ] `pytest -q` -- <pass/fail with count>
- [ ] `pyright .` (or `mypy .`) -- <pass/fail with count, or "n/a" if not configured>
- [ ] `ruff check .` -- <pass/fail>
- [ ] `git diff --name-only main..HEAD` matches `files.touched` in the task spec

## Acceptance criteria
<For each criterion listed in the task spec, restate it and provide evidence.>

- [ ] <criterion verbatim from task spec>
  Evidence: <command output, file paths, line numbers, or a one-line argument>

## Out-of-scope confirmation
- [ ] No files in `files.must-not-touch` were modified
  Evidence: `git diff --name-only main..HEAD` was cross-checked against the
  must-not-touch list.

## Things I deliberately did not do
<Anything that came up while doing the task but was outside scope. This is
the "while I was in here" honesty list. Saying "nothing" is fine if true.>

## Risks for human reviewer
<1-3 things the reviewer should think about. Concrete, not boilerplate.
"None identified" is a valid answer.>

## Diff summary
- N files changed, +M / -K lines
- <Highlights: what's new, what moved, what was renamed>

## Verdict
<One sentence: "Ready to merge" or "Needs rework: <reason>".>
