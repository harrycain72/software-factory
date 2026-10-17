# Deterministic recovery

Use this procedure for `/factory resume`, an interrupted run, unavailable recorded agents, dirty worktrees, or a discrepancy among state, Git, artifacts, and the hosting service. Acquire and retain the normal coordinator lock first. Recovery never authorizes a local `main` checkout, state destruction, a replacement job ID, or a bypass of pull-request protection.

## Reconcile in order

1. Parse schema-v2 `factory/board.json` and every managed backlog line. Match each `[~]` assignment to exactly one non-merged job and every `[x]` assignment to a merged job. Preserve historical merged records.
2. Inspect every `factory/jobs/<job-id>/` artifact expected by its stage. Validate first-line tokens, round numbers, slots, branches, and full SHAs. Artifacts may justify moving a board record only after all corresponding Git evidence agrees.
3. Enumerate registered worktrees and relevant refs. Verify each feature and release path and exact branch against the board. Assert that no factory worktree has `main` checked out and none is detached. If any does, stop for human inspection without changing it.
4. Inspect dirtiness. Never reset, clean, stash, commit, or discard unexplained changes. Record exact paths and stop the affected job; unrelated jobs may continue only when their state and locks are independent.
5. Reconstruct the saved worker ceiling and held locks. A lock remains held for every feature-created job not integrated or explicitly abandoned. Resolve duplicate lock ownership by stopping affected work, not by choosing a winner.
6. Reconcile recorded agent identities. Resume reachable identities. Recreate an unreachable role from the same absolute inputs and durable artifacts, retaining the job ID, logical builder name, branch, round, and output path; record the new provider identity in history.
7. If a pull request is recorded, query the hosting service and fetch `origin/main`. Compare PR base, head branch, head SHA, state, checks, approvals, and merge result to the board. Host and Git evidence override stale conversational claims.

## Stage reconstruction

- `queued`: no feature worktree is required. Start only if dependencies and locks are ready.
- `spec`: require or regenerate only `spec.md`; do not infer it from a message.
- `build`: require the feature worktree and branch. A valid `build.md` alone does not prove a commit; verify Git.
- `review`: preserve valid verdicts only when they match the current round, comparison SHA, and HEAD. Rerun missing, malformed, or stale reviews.
- `integrating` or `approval`: ensure no other job occupies either stage. Recheck release SHA; changed SHA invalidates review/approval and sends the job through update and a new round.
- `integrated`: prove the feature merge is on the release branch. Keep `[~]`; continue release publication or PR monitoring.
- `needs-human`: do not invent approval. Continue unrelated work and mark only true dependants blocked.
- `blocked`: recompute dependency status. Unblock only when all blockers are integrated in this release or proven on `origin/main`.
- `merged`: fetch and prove the approved job commit remains an ancestor of `origin/main`; otherwise stop on state corruption.

## Partial admission or integration

Unexpected refs, directories, registrations, commits, or half-written state require inspection. Do not delete or overwrite them. Determine the last operation proven complete, persist a diagnostic history entry only if the board can be safely and atomically updated, and ask a human to resolve ambiguity.

Never auto-remove a foreign or unreadable coordinator lock. Report its owner data and path. A human must establish that the owner is dead and explicitly authorize removal.

## Pull-request outcomes

- Open and healthy: persist current state and continue waiting or refreshing.
- Head changed outside the coordinator: stop for human inspection.
- Base advanced: merge fetched `origin/main` into the guarded release worktree and invalidate affected validation as specified in `SKILL.md`.
- Closed or rejected without merge: retain `integrated`; set `needs-human` where no automatic path remains.
- Host reports merged: fetch, verify each approved commit is an ancestor of `origin/main`, then and only then mark `merged`, update backlog `[x]`, remove the clean release worktree, and clear the batch.
