# AgentArchitect

The **AgentArchitect** is the first reference agent delivered for the Software Developer Agent Platform. It is designed to act as a subject-matter expert on building other agents inside this workspace.

## Purpose
- Analyse the current repository context (documentation, tools, tests, branch state).
- Produce actionable recommendations for standing up or evolving developer agents.
- Capture observations and guidance notes that can be fed into downstream planning sessions.

## Behaviour
| Phase | Description |
|-------|-------------|
| Plan  | Generates a five-step plan covering context review, tooling, capability design, milestone definition, and validation strategy. |
| Act   | For each plan step, gathers workspace metadata and emits targeted recommendations (e.g., which docs to read, which tests to codify). |
| Observe | Records a concise summary of recommendations prepared for the step. |
| After iteration | Stores structured notes under `state.artifacts["architecture_notes"]` for later review. |
| Summarise | Returns a sentence describing the completed plan and number of steps executed. |

## Inputs
The agent consumes a `TaskSpec` whose `metadata` may include:
- `workspace_docs`: Documentation paths to prioritise.
- `available_tools`: Human-readable description of registered tools.
- `test_commands`: Commands covering the regression suite.
- `branch`: Active branch name (defaults to `feature/version2`).
- `focus_area`: Specific aspect of agent development to emphasise.
- `knowledge_topics`: Optional list of knowledge-base files under `docs/agent_platform/knowledge/` to preload.

## Knowledge Base Integration
AgentArchitect should read the summaries stored in `docs/agent_platform/knowledge/` (e.g., OpenAI assistant capabilities, orchestration best practices, safety guidance) before generating plans.

## Extending
- Register additional tools in the `ToolRegistry` to enrich environment snapshots.
- Override or wrap the agent to integrate with live execution tools (e.g., code editors, git operations).
- Feed `architecture_notes` into ADRs or roadmap updates to create traceable planning artefacts.
