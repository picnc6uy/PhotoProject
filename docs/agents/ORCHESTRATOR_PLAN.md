# Orchestrator Plan

_Last updated: 2026-02-10_

## Goal
Provide a Python-first orchestration layer that coordinates agents, enforces caching, and guarantees structured artefacts for every run.

## Responsibilities
- Load knowledge base entries and pass relevant metadata into agent tasks.
- Resolve and initialise agent instances with the appropriate tool registry.
- Compute cache keys (agent + task + mode) and persist run artefacts.
- Execute the agent loop, capture `AgentState`, and serialize outputs.
- Log provenance data (timestamps, config snippets, tool list) for observability.
- Offer hooks for evaluation harnesses and future coordination with multiple agents.

## Key Components
1. **CacheStore**
   - Root folder (default `dev_data/agent_platform/cache`).
   - Methods: `make_key(agent_name, task)`, `load(key)`, `save(key, record)`.
   - Stores JSON containing task spec, agent config summary, agent state summary, timestamps.

2. **Orchestrator**
   - Constructor accepts `ToolRegistry`, cache directory, logger.
   - `run(agent, task, use_cache=True)`:
     1. Compute cache key.
     2. Return cached record if available.
     3. Execute agent, convert `AgentState` to serializable dict.
     4. Save record (if caching enabled), including plan, actions, artefacts.
     5. Return `(record, from_cache)` tuple.

3. **Record Schema**
   ```json
   {
     "agent": {"name": "AgentArchitect", "config": {...}},
     "task": {...},
     "state": {
       "iteration": 5,
       "plan": [...],
       "actions": [...],
       "artifacts": {...},
       "notes": [...],
       "outcome": "..."
     },
     "metadata": {
       "cache_key": "...",
       "created_at": "2026-02-10T22:34:00Z",
       "tools": ["echo: Echo command for testing"],
       "use_cache": true
     }
   }
   ```

## Testing Strategy
- Unit test: ensure orchestrator saves and loads cache; second run should avoid re-executing agent.
- Validate JSON structure contains expected fields.
- Use temporary directories for cache isolation.

## Next Steps
- Implement `orchestrator.py` with `CacheStore` and `Orchestrator` classes.
- Add unit tests (`src/tests/test_orchestrator.py`).
- Wire Orchestrator usage into future CLI/evaluation harness.
- Extend to multi-agent workflows after single-agent orchestration stabilizes.
