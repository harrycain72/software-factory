# Runtime dispatch adapters

Read this file only for provider discovery, role lifecycle calls, and model preflight. All scheduling, state, Git, validation, integration, and recovery rules remain in `SKILL.md` and `recovery.md`.

| Operation | Claude Code | Codex | GitHub Copilot |
|---|---|---|---|
| invoke factory | `/factory …` | `$factory …` or explicitly request the `factory` skill | `/factory …` |
| dispatch role | Agent tool with the matching `.claude/agents/` role | spawn the matching `.codex/agents/` custom agent | task/custom-agent tool with the matching `.github/agents/` role |
| follow up or resume | resume/send to the recorded named agent | follow up on the recorded agent thread | write to or resume the recorded custom-agent task |
| wait | wait for the recorded background agents | wait for the recorded subagents | read/wait for the recorded agent tasks |
| stop | stop the recorded named agent | interrupt the recorded subagent | stop the recorded custom-agent task |

## Preflight

Run `python3 factory/render-runtime-adapters.py --check`. Load `factory/runtime-models.json` and resolve the selected provider model for all seven roles. Query that provider's role discovery and model availability surfaces. Require exact equality between manifest, generated profile, and runtime-reported selected model. A missing role, unavailable model, provider fallback, inherited session model, or inability to prove the selected model stops the run.

The current policy resolves to:

| Role | Claude Code | Codex | GitHub Copilot |
|---|---|---|---|
| spec-writer | sonnet | gpt-5.6-terra | gpt-5.6-terra |
| builder | sonnet | gpt-5.6-terra | gpt-5.6-terra |
| reviewer-security | sonnet | gpt-5.6-terra | gpt-5.6-terra |
| reviewer-ux | sonnet | gpt-5.6-terra | gpt-5.6-terra |
| reviewer-ui | sonnet | gpt-5.6-terra | gpt-5.6-terra |
| reviewer-code | opus | gpt-5.6-sol | claude-opus-5.5 |
| approver | sonnet | gpt-5.6-terra | gpt-5.6-terra |

GitHub Copilot's configured Terra model is announced for retirement on 2026-11-16. Before that date, a human must update only `factory/runtime-models.json`, render, review, and deliver the resulting profiles through the factory. Never accept automatic fallback.

## Dispatch envelope

Every invocation receives, as explicit values rather than remembered prose:

- runtime role name and stable agent/thread/task identity;
- absolute repository-profile, worktree, job-directory, input, and sole output paths;
- exact recorded branch and full base/comparison/head SHAs;
- story ID, job ID, batch ID, review round, and held locks;
- the exact slot name and environment assignments from `factory/slot.sh`;
- validation commands from the profile;
- a reminder that board/backlog writes and model overrides are forbidden.

Record the provider-returned agent/thread/task identity in the job record before relying on it. Never set a spawn-time model. For rework, use follow-up/resume on `builder-<job-id>` rather than creating a replacement. If a recorded identity is unreachable, follow `recovery.md` and reconstruct from durable artifacts using the same logical identity.
