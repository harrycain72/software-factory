---
name: factory
description: Coordinate dependency-aware, isolated feature pipelines into a protected release-branch pull request. Use for /factory or $factory feature intake, backlog batches, resume, approval, or rework.
---
# Parallel software factory

Act as the single coordinator. The durable files and Git graph are authoritative; chat history and agent messages are not. Use runtime-neutral lifecycle operations in this file. Read [dispatch.md](dispatch.md) before dispatching any role or checking provider/model availability. Read [recovery.md](recovery.md) for `resume`, inconsistent state, failed processes, dirty worktrees, or pull-request reconciliation.

## Command surface

Accept only:

```text
/factory <feature>
/factory next [count] [--parallel workers]
/factory resume
/factory approve <job-id>
/factory rework <job-id> <note>
```

`$factory` is the equivalent Codex spelling. Treat `/factory <feature>` as adding one fully formed pending backlog story after assigning a stable story ID and explicit dependency and lock metadata; it does not bypass batching. `count` and `workers` are positive integers, `workers <= count`, and the default for both is 1 where omitted. Reject unknown flags or ambiguous input before writing.

## Non-negotiable invariants

- `main` is remote-owned. Never check it out locally, create work on it, commit or merge on it, or push to it. There are no setup, recovery, documentation, urgent-fix, or single-job exceptions.
- Product work occurs only on `factory/feature/<job-id>` in `.worktrees/<job-id>`. Batch integration occurs only on `factory/release/<batch-id>` in `.worktrees/<batch-id>-release`.
- Only the hosting service may merge the release pull request to `main`, using a strategy that preserves release commits as ancestors. Never squash or rebase the release PR.
- Exactly one coordinator writes `factory/board.json`, `factory/backlog.md`, factory bookkeeping commits, the release branch, or pull-request state.
- A worker never writes board or backlog state. One named `builder-<job-id>` owns each job across all rework.
- Hold each job's declared locks from feature-worktree creation until release integration or explicit human-approved abandonment.
- At most `active_batch.parallel` job pipelines are active. At most one job is in `integrating` or `approval`.
- `integrated` is not merged or done. Only a fetched proof that the approved job commit is an ancestor of `origin/main` permits `merged` and backlog `[x]`.
- Do not select or pass models at dispatch. Generated profiles and `factory/runtime-models.json` are the sole model policy.
- A dirty or surprising worktree is evidence. Never reset, clean, overwrite, delete, or auto-repair it.

## Entering every command

Perform this sequence even for `resume`, `approve`, and `rework`:

1. Resolve the repository root and invoking checkout's symbolic branch. Before any write, fail if it is detached or `main`. Run `sh factory/branch-guard.sh <invoking-checkout> <resolved-branch>` immediately before an allowed mutation.
2. Derive a unique owner token containing runtime, process/session identity, and random entropy. Run `sh factory/orchestrator-lock.sh acquire <owner>` before reading mutable factory state. Keep it for the entire orchestration run. Install handled-exit cleanup that calls `release` with the same token. Never remove a foreign, unreadable, or apparently stale lock.
3. Read `factory/repo.md`; fail if it lacks real Git hosting, pull-request, check, approval, merge-strategy, or project-command details needed for the requested operation.
4. Run `python3 factory/render-runtime-adapters.py --check`. Then use the selected provider's discovery mechanism to prove that all seven roles exist and each materialized model matches the manifest and is enabled for the current account or organization. Fail closed on any missing, stale, unavailable, or substituted model.
5. Fetch `origin main` without checking out `main` and resolve a full `origin/main` SHA. Require an `origin` remote and a committed `origin/main`.
6. Parse and validate the entire backlog and board before writing. Require board schema version 2.

Always release the owned coordinator lock on normal or handled error exit. An active background orchestration run retains it while workers execute.

## Backlog grammar and validation

Each story line is exactly:

```text
- [<state>] [EPIC: <name>][<story-id>][DEPENDS: <ids-or-none>][LOCKS: <names-or-none>] <feature text> [→ <job-id>]
```

States are `[ ]`, `[~]`, and `[x]`. Story IDs are unique `US-###` values. Dependencies are comma-separated story IDs or `none`; locks are comma-separated narrow names or `none`, with no duplicate name in one story. The optional assignment uses the Unicode arrow. Reject malformed managed lines, duplicate IDs, unknown dependencies, duplicate lock names, assignment/state mismatches, and dependency cycles before any state write. A legacy line lacking metadata may be migrated only as an exclusive job.

Backlog order is admission priority and the integration tie-breaker, never an implicit dependency. A job is ready only when every dependency is `integrated` in the current batch release or proven `merged` in fetched `origin/main`, and none of its locks intersects the locks of another non-terminal job.

## Durable state

The board has `schema_version: 2`, one `active_batch` or null, and `jobs`. The active batch records `id`, positive `parallel`, admitted story IDs, `release_branch`, full `release_base_sha`, and `pull_request` (null or number, URL, head SHA, and state).

Every job records `id`, `story_id`, `title`, `branch`, `batch_id`, `depends_on`, `locks`, full `base_sha`, `merge_order`, `stage`, `round`, `reviews`, `history`, `decision`, `note`, and UTC `updated`. Stages are `queued`, `spec`, `build`, `review`, `integrating`, `approval`, `integrated`, `blocked`, `needs-human`, and `merged`.

For every transition and review verdict, construct the complete next board in memory, write a temporary sibling under `factory/`, parse it back as JSON, fsync when available, and atomically rename it over `factory/board.json`. Update the corresponding durable job artifacts before advancing the board. Edit each selected backlog line atomically in the same coordinator step and validate it again. Record transitions and material facts in append-only `history` entries.

Never report an agent as successful until its required artifact exists, is confined to its declared output path, has the required first-line token, and agrees with the branch, SHAs, round, slot, and Git state. Missing or malformed output is a failed attempt.

## Admission transaction

Do not admit while `active_batch` is non-null. For `next`:

1. Fetch and save the full current `origin/main` SHA. Select the first `count` pending stories and validate the complete graph and locks.
2. Create a collision-resistant `batch-<UTC-basic>-<random>` ID. Reserve `factory/release/<batch-id>` and `.worktrees/<batch-id>-release`; fail on any unexpected existing ref, directory, or worktree registration.
3. From the fetched SHA, run `git worktree add <release-path> -b <release-branch> <release-base-sha>`. Guard the new worktree and branch.
4. Reserve consecutive zero-padded job numbers by considering both `factory/jobs/` and all board history. Never reuse an ID.
5. Create each job directory and complete queued record. Set the active batch, including its saved worker ceiling.
6. Change only the selected lines to `[~]` and append `→ <job-id>`.
7. Atomically persist the validated board and backlog. If any reservation or pre-persistence step fails, stop and report exact partial Git/filesystem state for human inspection; do not guess or delete it.

## Bounded scheduler

Repeatedly reconcile completed workers, validate their artifacts, update state, and fill free pipeline slots with dependency-ready, lock-compatible queued jobs in backlog order. A pipeline occupies a slot from feature-worktree creation through review readiness, rework, or an explicit wait for integration. Capacity limits worker pipelines, not the single serialized integration boundary.

For each newly ready job:

1. Capture the current full release-branch SHA as `base_sha`.
2. Guard the release worktree, then create `factory/feature/<job-id>` and `.worktrees/<job-id>` at that exact SHA. Fail on collisions and guard the result.
3. Mark `spec`, allocate a role slot, and dispatch `spec-writer` with absolute profile, worktree, branch, SHA, input, and output paths. Validate `spec.md`, drop only that exact slot, then mark `build`.
4. Resume or dispatch the single `builder-<job-id>` with the absolute feature worktree, exact branch/base, `spec.md`, `build.md`, profile, and isolated slot assignments. Validate a clean committed feature result and `build.md`; drop its slot.
5. Increment `round`, mark `review`, capture one immutable comparison SHA, allocate four distinct reviewer slots, and dispatch all four reviewers together when capacity permits. Queue reviewer processes if runtime capacity is lower without changing job readiness, locks, or merge order.
6. Validate every verdict and record it immediately. Drop a review slot only after its artifact exists. If any says CHANGES, send findings to the same builder identity for rework, require a new commit and build report, then start a fresh round against the exact comparison SHA. Never reuse verdicts across a changed HEAD.

A failed or `needs-human` job blocks only its dependants; set those dependants `blocked` with evidence and continue unrelated ready work. Do not release locks for a merely failed, blocked, or awaiting-human job unless a human explicitly abandons it.

## Serialized integration and approval

Choose PASS-reviewed jobs in dependency order and then original backlog order. Only one may cross this boundary:

1. Mark it `integrating`. Compare its saved `base_sha` with the current full release SHA.
2. If release advanced, guard the feature worktree, merge the release branch into the feature branch there, and send conflicts to its existing builder. Run the full isolated checks and a new four-reviewer round against the new exact comparison SHA. Never resolve feature conflicts in the release worktree.
3. Mark `approval`, allocate an approver slot, and dispatch `approver` with the same comparison SHA and current feature HEAD. Validate `decision.md`, then drop only that exact slot. ESCALATE becomes `needs-human`.
4. Immediately before merging, re-read the release SHA. If it differs from the approved comparison SHA, the decision is stale: return to step 2 and repeat validation, reviews, and approval.
5. Guard the recorded release worktree and merge the exact feature branch there with `--no-ff`. Never perform an implicit-current-branch merge.
6. Remove the completed feature worktree only after its clean committed contents and merge are proven; retain the feature branch. Record artifacts and any required profile/slot refresh in a factory bookkeeping commit on the release branch, after guarding it.
7. Mark `integrated`, keep backlog `[~]`, release exactly this job's locks, and fill newly available scheduler slots before selecting the next integration.

## Release publication

When every currently releasable admitted job is integrated and no unrelated job can advance:

1. Fetch `origin/main`. If it advanced beyond `release_base_sha`, guard the release worktree and merge the fetched remote SHA into the release branch there. Resolve conflicts only there, run the full slot-isolated suite, and invalidate/repeat every review or approval whose comparison no longer matches the receiving release SHA.
2. Guard and push only the exact `factory/release/<batch-id>` branch. Create or update one pull request with base `main` and that exact head. Persist its number, URL, head SHA, and state immediately.
3. Monitor configured required checks and human approvals. A hosting command may request merge after gates pass; it must never bypass protection, push `main`, or perform a local merge.
4. If remote `main` advances while the PR is open, refresh the release branch, rerun invalidated validation and approvals, push it, and persist the new head SHA.
5. A closed, rejected, or failing PR leaves jobs `integrated` or sets the affected state to `needs-human`; never call them merged.
6. After the host reports merged, fetch `origin/main` and run `git merge-base --is-ancestor <approved-job-sha> origin/main` for every integrated job. Only then mark each `merged`, set its backlog line `[x]`, remove the clean release worktree, and clear `active_batch`. Apply the recorded branch-retention policy without touching local `main`.

Stop automatically only when every admitted job is `merged`, `needs-human`, or `blocked` by a needs-human dependency and no release PR remains open or mergeable. Clear `active_batch` only at that terminal boundary; retain all job records and assignments so human commands can resume the same IDs. Otherwise continue publication/reconciliation or leave durable state for `resume` while releasing the coordinator lock at the end of the command.

## Human commands

`approve <job-id>` may resume a job awaiting a documented human decision; it does not substitute for the role approver, required hosting approval, tests, or stale-SHA checks. Record the human decision and evidence, then continue the same job ID and builder identity.

`rework <job-id> <note>` appends the note, returns the job to its existing builder, and creates a new review round after a new committed result. It never allocates another job or discards the existing worktree.
