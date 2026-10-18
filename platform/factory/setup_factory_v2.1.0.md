# Set up a parallel software factory

This guide turns a Git repository into a factory that can run independent job
pipelines concurrently from Claude Code, Codex, or GitHub Copilot. It is a
setup contract, not a second orchestrator implementation: the executable
operating rules have one canonical copy in `.claude/skills/factory/`, exposed
to the other runtimes through thin, generated adapters.

The resulting factory has one coordinator and many isolated workers:

```text
pending backlog
      |
      v
dependency + resource-lock scheduler
      |
      +-- job A: spec -> feature branch -> reviews --+
      +-- job B: spec -> feature branch -> reviews --+--> release branch -> PR -> main
      +-- job C: spec -> feature branch -> reviews --+
```

Parallelism applies to job pipelines. Admission state, the board, backlog
updates, approval against the latest `origin/main`, release-branch integration,
and pull-request publication have exactly one writer. Running several
orchestrators against the same checkout is not a way to increase capacity and
is explicitly prevented by a cross-session lock.

## Non-negotiable branch policy

`main` is protected and remote-owned. No human, coordinator, or agent may do
implementation, conflict resolution, bookkeeping, commits, or merges on a
local `main` branch or in a worktree whose checked-out branch is `main`. Never
push directly to `main`, even with `--force` or to repair a failed run.

All repository changes use both levels of isolation:

- each job is implemented and committed on `factory/feature/<job-id>` in its
  own feature worktree;
- each batch is assembled and validated on `factory/release/<batch-id>` in a
  dedicated release worktree; and
- the release branch reaches `main` only through a pull request reviewed and
  merged by the repository hosting service after required checks pass.

There is no single-job, urgent-fix, setup, documentation, bookkeeping, or
recovery exception. Even a one-commit batch uses a feature branch, a release
branch, and a pull request to reach `main`.

Fetching `origin/main`, reading it, comparing against it, and using its commit
SHA as a base are allowed. Checking out local `main` to make a change is not.
If any documented command, agent instruction, or recovery path would require a
local `main` checkout, stop and fix that workflow before admitting work. These
rules apply to factory setup and bookkeeping changes as well as product code.

## Prerequisites

- A Git repository with an `origin` remote and a committed `origin/main`.
- A repository hosting service that supports pull requests, required checks,
  approvals, and branch protection. Configure `main` to reject direct pushes
  and force pushes and to accept changes only through pull requests. Factory
  release pull requests must use a merge strategy that preserves their commits
  as ancestors of `main`; do not squash or rebase them.
- Claude Code, Codex, or GitHub Copilot with support for repository skills and
  named custom agents. Enable every runtime that contributors may use; a
  repository may support one, two, or all three.
- Project-specific install, test, and check commands that work non-interactively.
- Enough local resources for the selected worker count.
- Per-worker isolation for every shared service the tests use (database,
  queue, browser, ports). This repository starts without a stack, so
  `factory/slot.sh` allocates only the slot name until a job adds more.

Do not enable parallel jobs until the serial project test and check commands
pass. Parallel execution amplifies nondeterminism and shared-state bugs; it does
not repair them.

## Files to create

Create this layout from the repository root:

```text
.agents/
  skills/
    factory -> ../../.claude/skills/factory   # Codex entry point; symlink
.claude/
  agents/
    spec-writer.md
    builder.md
    reviewer-security.md
    reviewer-ux.md
    reviewer-ui.md
    reviewer-code.md
    approver.md
  skills/factory/
    SKILL.md                                  # canonical coordinator contract
    dispatch.md
    recovery.md
.codex/
  config.toml
  agents/
    spec-writer.toml
    builder.toml
    reviewer-security.toml
    reviewer-ux.toml
    reviewer-ui.toml
    reviewer-code.toml
    approver.toml
.github/
  agents/
    spec-writer.agent.md
    builder.agent.md
    reviewer-security.agent.md
    reviewer-ux.agent.md
    reviewer-ui.agent.md
    reviewer-code.agent.md
    approver.agent.md
factory/
  runtime-models.json
  render-runtime-adapters.py
  backlog.md
  board.json
  dashboard.html
  branch-guard.sh
  orchestrator-lock.sh
  repo.md
  slot.sh                    # per-agent test resource allocator
  jobs/                      # generated job records
.worktrees/                  # generated, ignored by Git
```

GitHub Copilot discovers project skills in `.agents/skills/`, so do not create
a third copy under `.github/skills/`. Claude uses the canonical `.claude`
directory, and Codex follows the `.agents/skills/factory` symlink. If the
platform or checkout cannot preserve symlinks, generate a byte-for-byte copy
and make `render-runtime-adapters.py --check` reject drift from the canonical
directory.

Add `.worktrees/`, the orchestrator lock directory, per-slot coverage files,
and per-slot tool caches to `.gitignore`. Factory job records are durable and
must remain tracked.

The files in this repository are working reference implementations. Copy their
structure when bootstrapping another repository, then adapt only the project
profile, commands, shared-resource allocator, and agent expertise. Treat
`.claude/skills/factory/`, `.claude/agents/`, `factory/runtime-models.json`,
and `render-runtime-adapters.py` as source files; the `.codex/agents/` and
`.github/agents/` profiles are generated artifacts.

Bootstrap or change these factory-owned files on a normal feature branch and
deliver them through a release-branch pull request. The fact that setup files
coordinate the factory does not exempt them from the branch policy.

## Runtime adapters and enforced models

Keep orchestration logic and role prompts DRY:

- `.claude/skills/factory/` is the only copy of the coordinator workflow.
- The Markdown body of each `.claude/agents/<role>.md` is the canonical role
  contract. Provider adapters carry only provider metadata and an instruction
  to load and follow that canonical body.
- `factory/runtime-models.json` is the only editable model-routing policy.
  `factory/render-runtime-adapters.py` renders all provider profiles and its
  `--check` mode fails when generated files are missing or stale.
- Never hand-edit a generated Codex or Copilot agent profile. Change the
  canonical Claude role contract or the model manifest, render, and review the
  resulting diff.

Use this model manifest exactly unless a human explicitly changes the factory
policy:

```json
{
  "defaults": {
    "claude": "sonnet",
    "codex": "gpt-5.6-terra",
    "github-copilot": "gpt-5.6-terra"
  },
  "overrides": {
    "reviewer-code": {
      "claude": "opus",
      "codex": "gpt-5.6-sol",
      "github-copilot": "claude-opus-5.5"
    }
  }
}
```

The renderer has two modes:

```sh
python3 factory/render-runtime-adapters.py          # render deterministically
python3 factory/render-runtime-adapters.py --check  # read-only drift check
```

It discovers exactly the seven canonical Claude role files listed above,
preserves each Markdown body byte-for-byte, resolves the default plus any role
override from the manifest, updates only the Claude frontmatter metadata, and
renders the matching Codex and Copilot adapters. Write generated files through
temporary siblings and atomic renames. `--check` renders in memory and exits
non-zero for an unknown/missing role, invalid manifest, wrong model, changed
canonical-body pointer, missing adapter, or any byte-level output difference.
Generation must be deterministic so a second render produces no diff.

The renderer must materialize the resolved model in every agent profile, not
merely rely on the parent session's selected model. This prevents an
interactive model choice from silently changing a factory role. The resolved
matrix is:

| Agent | Claude Code | Codex | GitHub Copilot |
|---|---|---|---|
| `spec-writer` | `sonnet` | `gpt-5.6-terra` | `gpt-5.6-terra` |
| `builder` | `sonnet` | `gpt-5.6-terra` | `gpt-5.6-terra` |
| `reviewer-security` | `sonnet` | `gpt-5.6-terra` | `gpt-5.6-terra` |
| `reviewer-ux` | `sonnet` | `gpt-5.6-terra` | `gpt-5.6-terra` |
| `reviewer-ui` | `sonnet` | `gpt-5.6-terra` | `gpt-5.6-terra` |
| `reviewer-code` | `opus` | `gpt-5.6-sol` | `claude-opus-5.5` |
| `approver` | `sonnet` | `gpt-5.6-terra` | `gpt-5.6-terra` |

Render provider files as follows:

- **Claude Code:** `.claude/agents/<role>.md` uses YAML frontmatter with
  `name`, `description`, `tools`, and the resolved `model`. Its Markdown body
  is the canonical role contract.
- **Codex:** `.codex/agents/<role>.toml` sets `name`, `description`, the
  resolved `model`, and `developer_instructions`. The instructions tell the
  agent to read `.claude/agents/<role>.md`, ignore that file's YAML
  frontmatter, and follow its Markdown body as the role contract. Set
  `[agents] enabled = true` in `.codex/config.toml`; do not set or pass a
  competing spawn-time model.
- **GitHub Copilot:** `.github/agents/<role>.agent.md` uses YAML frontmatter
  with `name`, `description`, `tools`, `include-custom-instructions: true`,
  and the resolved `model`. Its short body tells the agent to read and follow
  the Markdown body of `.claude/agents/<role>.md`.

The canonical coordinator contract must use runtime-neutral operations such as
"dispatch role", "send follow-up", "wait", and "stop". Put the concrete
mapping in `dispatch.md`:

| Operation | Claude Code | Codex | GitHub Copilot |
|---|---|---|---|
| invoke factory | `/factory …` | `$factory …` (or explicitly request the `factory` skill) | `/factory …` |
| dispatch role | Agent tool with the `.claude/agents/` role | spawn the matching `.codex/agents/` custom agent | task/custom-agent tool with the `.github/agents/` role |
| follow up or resume | resume/send to the recorded named agent | follow up on the recorded agent thread | write to or resume the recorded custom-agent task |
| wait | wait for the recorded background agents | wait for the recorded subagents | read/wait for the recorded agent tasks |

Provider adapters must not reimplement scheduling, recovery, validation, or
integration rules. They translate only invocation and agent lifecycle calls.
Every provider records the returned agent/thread/task identity in the same
board field, so `/factory resume` remains runtime-neutral. A resumed batch may
use a different supported provider, reconstructing unreachable agents from
durable files as described below.

During preflight, run `render-runtime-adapters.py --check`, verify the selected
provider exposes all seven roles, and verify every configured model is enabled
for the current account or organization. Fail closed on a missing model; never
fall back to the session model or another provider model. GitHub has announced
the retirement of GPT-5.6 Terra on 2026-11-16, so update the single manifest
and regenerate adapters before that date if this policy is still in use; do
not allow Copilot to choose a fallback automatically.

## 1. Record the repository contract

Write `factory/repo.md` before admitting work. It is the stable hand-off from
the coordinator to every agent and must state:

- product requirements and design sources;
- language, framework, and package layout;
- exact install, test, lint, format, and type-check commands;
- database, queue, browser, port, cache, and other shared-resource behavior;
- conventions and prohibited operations;
- the protected `main` policy, allowed feature/release branch patterns,
  pull-request command or API, required checks and approvals, and merge
  strategy;
- paths owned by the factory rather than feature branches, including
  `.agents/`, `.claude/`, `.codex/`, `.github/agents/`, `factory/`,
  `AGENTS.md`, and the factory contract tests;
- files that require resource locks, such as migrations, dependency manifests,
  generated clients, Compose configuration, and the repository profile itself.

Refresh the profile after an integrated job changes any of those facts. Agents
receive the path to the profile; the coordinator does not paste a remembered
summary of it into prompts.

## 2. Make dependencies and conflicts explicit

Use one parseable backlog line per story:

```markdown
- [ ] [EPIC: Foundation][US-004][DEPENDS: US-003][LOCKS: migrations,dependencies] Implement an append-only event store.
```

The grammar is:

```text
- [<state>] [EPIC: <name>][<story-id>][DEPENDS: <ids-or-none>][LOCKS: <names-or-none>] <feature text> [-> <job-id>]
```

Use the Unicode arrow `→` in the real backlog rather than the ASCII arrow in
the grammar sketch above. The fields mean:

- `[ ]`: pending; `[~]`: admitted, active, integrated into a release, blocked,
  or awaiting a human; `[x]`: confirmed present in `origin/main` after the
  release pull request was merged.
- `US-###`: a unique, stable story identifier.
- `DEPENDS`: stories that must be integrated into the current release branch
  or confirmed present in `origin/main` before this job can start.
- `LOCKS`: shared repository resources this job may change. Two active jobs
  with any lock in common must not overlap.
- `→ <job-id>`: assigned atomically when a story is admitted.

Backlog order is priority and the tie-breaker for integration; it is not an
implicit dependency. Encode every real dependency. Keep lock names narrow:
`migrations` is useful, while making every job `exclusive` defeats parallelism.
A legacy line without metadata may be accepted during migration, but it must
run exclusively.

Before writing any state, validate unique story IDs, known dependencies,
unique lock names per story, and an acyclic dependency graph. A story is ready
only if all its dependencies are already `integrated` into the current release
branch or `merged` into `origin/main`, and its locks do not overlap those held
by another non-terminal job.

## 3. Initialize the durable board

Create `factory/board.json` with schema version 2:

```json
{
  "schema_version": 2,
  "active_batch": null,
  "jobs": []
}
```

An active batch records the admitted stories and the concurrency ceiling:

```json
{
  "id": "batch-20261017T190000Z-a1b2",
  "parallel": 3,
  "admitted": ["US-004", "US-005", "US-014"],
  "release_branch": "factory/release/batch-20261017T190000Z-a1b2",
  "release_base_sha": "<full-origin-main-sha>",
  "pull_request": null
}
```

Each job record must include `id`, `story_id`, `title`, `branch`, `batch_id`,
`depends_on`, `locks`, `base_sha`, `merge_order`, `stage`, `round`, `reviews`,
`history`, `decision`, `note`, and `updated`. Valid stages are `queued`, `spec`,
`build`, `review`, `integrating`, `approval`, `integrated`, `blocked`,
`needs-human`, and `merged`. `integrated` means the feature commit is on the
release branch but is not yet on `main`; it must never be reported as merged or
done. `merged` is valid only after the pull request is merged and a fetch proves
the job's approved commit is an ancestor of `origin/main`.

Only the coordinator writes the board or backlog. Write the complete board to
a temporary file in `factory/`, parse it to verify valid JSON, then atomically
rename it over `board.json`. Update it at every state transition and whenever a
review verdict arrives so `/factory resume` can recover from files rather than
conversation memory.

## 4. Enforce one coordinator

Install `factory/orchestrator-lock.sh`. Every factory command, including
`resume`, `approve`, and `rework`, must:

1. resolve the invoking checkout's symbolic branch and fail before writing
   anything if it is `main` or detached;
2. derive a unique owner token;
3. run `sh factory/orchestrator-lock.sh acquire <owner>` before reading and
   mutating factory state;
4. keep the lock for the command's whole orchestration run;
5. run `sh factory/orchestrator-lock.sh release <owner>` on normal and handled
   error exits.

An occupied lock reports its owner and stops the second coordinator. Never
delete a foreign or apparently stale lock automatically. A human must inspect
and confirm stale-lock removal after a crashed process.

This lock serializes coordinators, not workers. The lock owner may keep several
job agents running concurrently while remaining the sole state writer.

## 5. Isolate every batch and job in Git

Install `factory/branch-guard.sh` as a shared fail-closed assertion and call it
from every coordinator and agent entry point before any operation that can
write a file, commit, ref, or remote state. Its essential behavior is:

```sh
current_branch=$(git -C "<worktree>" symbolic-ref --quiet --short HEAD) || exit 1
test "$current_branch" != main || exit 1
test "$current_branch" = "<recorded-expected-branch>" || exit 1
```

Use actual validated paths and recorded branch values in the implementation;
the placeholders above are contract notation, not commands to paste literally.
The initial command invocation is subject to the same `main`/detached-head
rejection even before a batch release worktree exists.

At admission, fetch the remote and resolve the full `origin/main` SHA without
checking out `main`. Save it as `release_base_sha`, then create one release
branch and one dedicated release worktree for the batch:

```sh
git fetch origin main
git worktree add .worktrees/<batch-id>-release \
  -b factory/release/<batch-id> <release-base-sha>
```

When a queued job becomes dependency-ready, capture the current full release
branch SHA as its `base_sha`, then create its feature branch and worktree:

```sh
git worktree add .worktrees/<job-id> \
  -b factory/feature/<job-id> <base-sha>
```

The release worktree is the only integration worktree. It must have
`factory/release/<batch-id>` checked out, never `main`. Before every operation
that can create a commit, assert the current branch explicitly and stop if it
is `main`, detached, or different from the branch recorded on the board. Apply
the same guard in feature worktrees. Do not use `git switch main`,
`git checkout main`, a local `main` worktree, or an implicit current branch in
automation.

There is exactly one builder identity per job, named `builder-<job-id>`. Resume
that builder for rework so ownership and context do not drift. Feature agents
may modify and commit only in their feature worktree. They must not edit any
factory-owned path (`.agents/`, `.claude/`, `.codex/`, `.github/agents/`,
`factory/`, `AGENTS.md`, or the factory contract tests), the release worktree,
any local `main` checkout, the backlog, or the board.

Give every agent explicit absolute paths, branch name, comparison SHA, output
file, validation commands, and runtime role name. Do not rely on its current
working directory or on prose copied from factory-owned files. Do not pass a
model at dispatch time: the generated role profile owns model selection.

The coordinator may create factory bookkeeping commits only on the recorded
release branch in its release worktree. No setup, recovery, cleanup, or
bookkeeping exception permits a local commit on `main`.

## 6. Isolate tests and shared resources

Separate worktrees do not isolate databases, ports, caches, coverage files, or
external sandboxes. Allocate a unique lowercase slot to every builder,
reviewer, and approver invocation:

```text
<job-number>_<role>[_r<round>]
004_builder
004_security_r1
004_approver_r2
```

Allocate and release per-slot resources with `factory/slot.sh`, which prints
the environment assignments the agent must use:

```sh
sh factory/slot.sh create <slot>     # prints KEY=value lines, e.g. FACTORY_TEST_SLOT=<slot>
<assignments> <factory test command from repo.md>
<assignments> <factory check command from repo.md>
sh factory/slot.sh drop <slot>
```

The factory test and check commands recorded in `factory/repo.md` must route
all mutable outputs through the slot: database name, coverage data, and test,
lint, and type-check caches. Never run parallel agents against a default test
database. Release only the resources derived from the exact slot after the
agent has completed and its required artifact exists.

Product-job feature branches never edit factory-owned paths. Dedicated factory
maintenance feature branches may change them, but those changes still flow
through a release branch and pull request. When a job adds a shared service
(for example PostgreSQL), its builder describes the per-slot create and drop
steps under `## Factory isolation` in `build.md`, and the coordinator applies
them to `slot.sh` together with the `repo.md` refresh in the bookkeeping commit.
Such jobs hold the `repo-profile` lock. A PostgreSQL reference is
`factory/test-db.sh` in the original factory repository.

For another stack, implement the same lifecycle for every shared mutable
resource. If a resource cannot be isolated, represent it as a backlog lock so
jobs using it are serialized.

## 7. Define narrow agent contracts

Each canonical agent file must define one owner and one durable output. The
Codex and GitHub Copilot profiles are generated adapters around these same
contracts; they do not carry independent copies of the instructions:

| Agent | Writes | Required outcome |
|---|---|---|
| spec writer | `factory/jobs/<id>/spec.md` | Testable scope and acceptance criteria |
| builder | feature worktree and `build.md` | Committed implementation with isolated checks |
| security reviewer | `round-<n>/review-security.md` | `VERDICT: PASS` or `VERDICT: CHANGES` |
| UX reviewer | `round-<n>/review-ux.md` | Same verdict contract |
| UI reviewer | `round-<n>/review-ui.md` | Same verdict contract |
| code reviewer | `round-<n>/review-code.md` | Same verdict contract |
| approver | `decision.md` | First line `APPROVE` or `ESCALATE` |

Reviewers compare `<comparison-sha>...HEAD`, never an implicitly moving branch.
Launch the four reviewers for a round together when agent capacity permits.
If the runtime cannot accommodate `4 x active jobs`, queue reviewer processes
without changing job readiness, lock ownership, or merge order.

Before dispatching, resolve the provider profile for the requested role and
assert its materialized model matches `factory/runtime-models.json`. A missing
profile, stale generated adapter, unavailable model, or runtime-selected model
that differs from the profile is a failed preflight, not permission to inherit
or fall back.

Agents do not update board state. The coordinator validates each output and
records its result. Missing or malformed output is a failed agent attempt, not
an inferred pass.

## 8. Implement the bounded scheduler

The factory command surface is:

```text
/factory <feature>
/factory next [count] [--parallel workers]
/factory resume
/factory approve <job-id>
/factory rework <job-id> <note>
```

Both `count` and `workers` are positive integers, and `workers` must not exceed
`count`. The default worker count is 1 so existing usage remains safe. For
example, `/factory next 6 --parallel 3` admits six backlog items and runs at
most three dependency-ready, lock-compatible job pipelines at once.

Admission is one transaction-like coordinator operation:

1. Fetch `origin/main`, select the first `count` pending stories, and validate
   their metadata.
2. Reserve the batch release branch from the fetched `origin/main` SHA and
   create its release worktree; fail if that branch or worktree already exists
   unexpectedly.
3. Reserve consecutive job numbers using both existing job directories and
   board records.
4. Create all job directories and queued board records.
5. Set the batch with its worker limit, release branch, release base SHA, and
   empty pull-request field.
6. Change each selected backlog line to `[~]` and append its job ID.

Then repeatedly fill free worker slots with ready jobs and advance each job
independently through spec, build, and review. A failed or `needs-human` job
blocks only its dependants. Unrelated ready jobs continue. Hold resource locks
from feature-worktree creation through release-branch integration or explicit
abandonment.

The coordinator stops automatically only when every admitted job is `merged`,
`needs-human`, or `blocked` by a needs-human dependency. Jobs that are merely
`integrated` have not reached a terminal state: the coordinator must still
publish, monitor, and reconcile the release pull request. Clear `active_batch`
only when no admitted job can advance automatically and no release pull request
remains open or mergeable.

## 9. Serialize integration and approval

Parallel feature work converges through one integration slot on the recorded
release branch. Choose completed jobs in dependency order, then original
backlog order, and allow only one job to be `integrating` or `approval`.

For the selected job:

1. Compare its `base_sha` with the current release-branch SHA.
2. If the release branch advanced, merge the release branch into the feature
   worktree and run a fresh review round against that exact SHA. Resolve
   conflicts through the job's builder and re-review; never resolve them in
   the release worktree or a local `main` checkout.
3. Run the approver with an isolated test slot and the same comparison SHA.
4. Immediately before integration, verify the release branch still equals the
   approved comparison SHA. If it changed, the approval is stale; update the
   feature branch and review again.
5. Assert that the release worktree has the recorded
   `factory/release/<batch-id>` branch checked out, then merge the feature
   branch there with `--no-ff`. Remove the feature worktree, retain the feature
   branch, and record job artifacts plus refreshed factory files in a
   bookkeeping commit on the release branch.
6. Mark the job `integrated`, keep its backlog entry `[~]`, release its locks,
   unblock dependants, and fill free worker slots before integrating the next
   completed job.

This serialized boundary is what makes concurrent builds safe: every accepted
result is tested and approved against the exact release commit that receives
it.

When every releasable job in the batch is integrated, publish the batch without
ever checking out or committing on local `main`:

1. Fetch `origin/main`. If it advanced beyond `release_base_sha`, merge
   `origin/main` into the release branch in the release worktree, run the full
   factory test/check suite, and repeat any review or approval invalidated by
   the changed comparison SHA. Conflict resolution stays on the release branch.
2. Push `factory/release/<batch-id>` and create or update a pull request whose
   base is `main` and whose head is that exact release branch. Persist the pull
   request number, URL, head SHA, and state in `active_batch.pull_request`.
3. Require the repository's configured checks and human approvals. A command
   such as `gh pr merge` may ask the hosting service to merge the pull request
   after those gates pass; it is not permission to perform a local merge or a
   direct push to `main`.
4. If `origin/main` changes while the pull request is open, refresh the release
   branch from the new remote SHA, rerun invalidated validation and approval,
   push the release branch, and update the recorded head SHA. Never make the
   pull request mergeable by bypassing protection.
5. After the hosting service reports the pull request merged, fetch
   `origin/main` and verify every approved job commit is its ancestor. Only then
   mark the jobs `merged`, change their backlog entries to `[x]`, remove the
   release worktree, and clear the active batch. Retain or delete remote feature
   and release branches according to repository policy.

Feature branches must not open pull requests directly to `main` in this model;
they integrate into the batch release branch. The release pull request is the
only path to `main`. A closed, rejected, or failing pull request leaves its jobs
`integrated` or `needs-human`, never `merged`.

## 10. Make restart behavior deterministic

`/factory resume` must reconcile, in this order:

- `factory/board.json` and `[~]` backlog entries;
- job directories and required stage artifacts;
- feature and release branches plus their registered worktrees;
- the batch's saved parallel limit and held resource locks;
- the recorded pull request against the hosting service and the fetched
  `origin/main` SHA.

Recreate an unreachable agent from durable files and paths; never allocate a
replacement job ID or reconstruct state from chat history. A dirty worktree is
evidence to inspect, never something to reset or discard automatically. Resume
must assert that no factory worktree has `main` checked out. If one does, stop
for human inspection; do not continue work there or try to normalize it with a
commit, reset, merge, or force push.

## Migrating an existing serial factory

1. Stop admitting work under any workflow that commits or merges on local
   `main`. Move unfinished changes to named feature branches before continuing.
2. Let every old-format non-terminal job reach a safe feature-branch commit or
   `needs-human`; deliver completed legacy work through a release pull request.
3. Tag the last already-published serial commit so rollback and comparison
   remain simple.
4. Add stable story IDs plus `DEPENDS` and `LOCKS` metadata to the backlog.
5. Upgrade the board to schema version 2 and preserve historical merged jobs.
6. Add the cross-session lock, release/feature worktree lifecycle, and
   pull-request state, plus shared-resource
   allocators.
7. Add slot-aware test/check commands and update every agent contract.
8. Replace the serial orchestration loop with bounded scheduling, serialized
   release integration, and pull-request-only publication to `main`.
9. Enable and verify branch protection before allowing the new coordinator to
   publish a release.
10. Run the verification below with concurrency 2 before choosing a larger
   default or batch limit.

Do not migrate board formats while an old job is actively changing state.

## Verification

Run the repository's factory contract tests first, once a job has added them
(for example `tests/test_factory_orchestration.py`). Then exercise a disposable
two-job batch whose stories have no dependency or lock conflict:

```text
/factory next 2 --parallel 2
```

Verify all of the following from files and process state, not only from agent
messages:

- one orchestrator owns the cross-session lock;
- the batch receives one unique release branch and release worktree based on
  the fetched `origin/main` SHA;
- both jobs receive different IDs, feature branches, and feature worktrees;
- no factory worktree has `main` checked out, and attempting to run on `main`
  fails closed before any file or ref is changed;
- `factory/branch-guard.sh` rejects `main`, detached HEAD, and every branch
  other than the exact feature or release branch recorded on the board;
- both may be in `spec`, `build`, or `review` at the same time;
- their agents receive different test slots and databases;
- the board remains valid JSON throughout polling;
- a third job with an overlapping lock remains queued;
- a dependant remains queued until its dependency is integrated into the same
  release or is confirmed in `origin/main`;
- no more than one job enters `integrating` or `approval`;
- an approval becomes stale and is rerun if the release branch changes;
- one job failure does not stop an unrelated job;
- `/factory resume` continues the saved batch without new IDs;
- integrated jobs remain `[~]` and are not marked `merged` before publication;
- the release branch is pushed and a pull request with base `main` is recorded;
- required pull-request checks and approvals cannot be bypassed, and a direct
  push to `main` is rejected by branch protection;
- if `origin/main` advances while the pull request is open, the release is
  refreshed and its invalidated validation is rerun;
- after the hosting service merges the pull request, a fetch proves
  `origin/main` contains both approved job commits before their state becomes
  `merged` and their backlog entries become `[x]`;
- completed feature and release worktrees are removed without checking out or
  updating a local `main` branch;
- the backlog, board, job artifacts, and repository profile agree.
- `render-runtime-adapters.py --check` passes and all three runtimes discover
  the same canonical `factory` skill;
- Claude Code, Codex, and GitHub Copilot each discover all seven roles;
- a dry-run dispatch for every non-code-review role reports Sonnet, Terra, and
  Terra respectively, while `reviewer-code` reports Opus, Sol, and Opus;
- changing a canonical role body or the model manifest makes adapter `--check`
  fail until the profiles are regenerated;
- selecting a different parent/session model does not change any factory
  agent's resolved model.

The setup is parallel-capable only when these invariants hold. Merely spawning
multiple agents, without worktree, resource, state-writer, and integration
isolation, is unsafe concurrency rather than a parallel factory.
