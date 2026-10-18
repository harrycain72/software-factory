# Repository contract

## Product and design sources

- Business requirements: `docs/solution/business-prd.md`.
- Technical requirements: `docs/solution/technical-prd.md`.
- Domain terminology: `docs/solution/GLOSSARY.md`.
- Domain map: `docs/solution/domain-map.md`.
- Feature and acceptance-criteria backlog: `docs/planning/epics-and-user-stories.md`. This is the source a human draws from when admitting a story with `/factory <feature>`; it does not populate `factory/backlog.md` automatically and is not read by the coordinator on its own.
- No design system or external design source has been configured yet.

## Architecture rules

Supplementary, binding conventions for specific kinds of change, cited by file path rather than restated here. Apply every rule file whose scope matches the change under implementation; record an exception in the pull request when a rule cannot apply, together with the reason and client impact.

- `docs/architecture/rules/api-endpoint-design.md` — all FastAPI HTTP endpoints: server-rendered pages, forms, downloads, health checks, and the JSON extraction API.
- `docs/architecture/rules/test-driven-development.md` — every story with testable behavior; applies by default, with exceptions recorded in the pull request rather than the backlog.
- `docs/architecture/rules/bce-architecture.md` — all product code: business-domain partitioning with Boundary–Control–Entity inside each domain, dependency direction, cross-domain contracts, and the default test seams. Its "Domain map" rule is applied through `docs/solution/domain-map.md`, which decides which domain owns each story's code.

`spec-writer` must name the applicable rule files in `spec.md` for the story. `builder` must follow them when implementing. `reviewer-code`'s check of "compliance with repository conventions" includes every rule file listed here, and a finding that cites one must name the specific rule.

## Stack and layout

- Language: Python 3.9+ for adapter generation and contract tests; POSIX `sh` for guards and resource allocation.
- Framework: none.
- Product package layout: not configured.
- Factory-owned paths: `.agents/`, `.claude/`, `.codex/`, `.github/agents/`, `factory/`, `AGENTS.md`, and `tests/test_factory_orchestration.py`.

## Commands

Run commands from the repository root with the slot assignments printed by `sh factory/slot.sh create <slot>`.

- Install: `:`
- Test: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'`
- Lint: `sh -n factory/branch-guard.sh && sh -n factory/orchestrator-lock.sh && sh -n factory/slot.sh`
- Format check: `python3 factory/render-runtime-adapters.py --check`
- Type/syntax check: `python3 -c "import ast,pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ('factory/render-runtime-adapters.py','tests/test_factory_orchestration.py')]"`
- Full factory check: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' && sh -n factory/branch-guard.sh && sh -n factory/orchestrator-lock.sh && sh -n factory/slot.sh && python3 factory/render-runtime-adapters.py --check`

Do not admit parallel product work until real product install, test, lint, format, and type-check commands replace or extend this bootstrap profile and pass serially.

## Shared resources

There is no database, queue, browser, fixed port, or external sandbox. `factory/slot.sh` currently reserves a unique slot and exports only `FACTORY_TEST_SLOT`. Python bytecode is disabled in checks. Coverage, future tool caches, and temporary outputs must use `.coverage.<slot>`, `.factory-cache/<slot>/`, and `.factory-tmp/<slot>/` respectively; those paths are ignored.

If a job adds a shared service, it must hold the `repo-profile` lock, document exact per-slot create/drop behavior under `## Factory isolation` in `build.md`, and update this profile plus `factory/slot.sh` in the release bookkeeping commit.

## Git and hosting policy

- `main` is protected, remote-owned, and must never be checked out locally for work, committed on, merged on, or pushed to directly.
- Feature branches are `factory/feature/<job-id>` and release branches are `factory/release/<batch-id>`.
- Every feature and release branch has its own worktree under `.worktrees/`.
- The sole path to `main` is a release-branch pull request with base `main`.
- The merge strategy must preserve release commits as ancestors of `main`; squash and rebase merges are prohibited.
- Hosting provider: GitHub.
- Origin: `https://github.com/harrycain72/software-factory.git`.
- Pull-request command after authentication and after `origin/main` exists: `gh pr create --base main --head <exact-release-branch> --fill`.
- Merge strategy: GitHub merge commit only, preserving every release commit as an ancestor of `main`; squash and rebase merges are prohibited.
- Branch retention: retain feature and release branches until the merged result is fetched and verified; remote deletion policy remains to be chosen by a human.
- Required checks, required human approvals, and branch protection are not yet configured. The supplied origin currently advertises no `HEAD` or `main` ref, and GitHub CLI is not authenticated. Factory preflight must fail closed until a human creates the remote-owned initial `main`, enables protection, defines the required gates, and records them here.

## Conventions and prohibited operations

- Use complete SHAs for bases and comparisons.
- Review `<comparison-sha>...HEAD`; never compare against an implicitly moving ref.
- The coordinator alone writes the board and backlog.
- Agents never update board or backlog state and never touch a local `main` checkout.
- Never reset, clean, discard, or overwrite a dirty worktree during recovery.
- Never pass a model at dispatch time. Generated profiles own model selection.
- Never infer success from an agent message; validate the required artifact and Git state.

## Resource locks

Use the narrowest applicable names. At minimum:

- `dependencies`: dependency manifests and lockfiles.
- `migrations`: schema and migration files.
- `generated-clients`: generated API clients and their schemas.
- `compose`: Compose and shared-service configuration.
- `repo-profile`: `factory/repo.md`, slot lifecycle, factory contract tests, or facts recorded in this profile.
- `factory-core`: any other factory-owned path.
