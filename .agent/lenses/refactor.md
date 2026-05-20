# Refactor lens

## Mindset
You are restructuring code without changing behavior. Tests should not
need modification. If a test changes, that's a behavior change -- either
justify it explicitly in the task spec or revert it.

## Required actions
1. Note the public API surface at the start of the task. Anything in
   `__all__`, any module-level export, or anything imported by external
   callers must remain identically callable after the refactor.
2. Make changes in small, individually-passing commits. Each commit on
   the branch must compile and pass tests on its own.
3. Run the full test suite after every commit, not just at the end.
4. Diff inspection: every changed line should be either (a) a structural
   move or (b) clearly the same logic in a different shape. New logic
   means you've added behavior; add a test for it or revert.

## Red flags
- Test count drops: you removed a test instead of moving it.
- New conditional branches: you added behavior; that's not a refactor.
- Import changes outside the area being refactored: you broke the
  contract someone else relied on.
- `# TODO: actually do this later` comments left in shipped code.

## Sanity check before verification
```bash
# Same test count and outcomes before and after.
git stash && pytest -q && git stash pop
pytest -q
```

The numbers must match. Document any difference with a justification.

## Output expectations
In the verification doc:
- Cite the test count before and after explicitly.
- List public-API symbols that survived the refactor (names, not paths).
- Note any test that was renamed or relocated and where it lives now.
