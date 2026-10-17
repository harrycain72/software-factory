# Factory bootstrap status

The parallel-factory files were authored from scratch for this workspace. The canonical coordinator contract is `.claude/skills/factory/`; provider role adapters are generated from `.claude/agents/` and `factory/runtime-models.json`.

## Current gate

This directory was initially not a Git repository. It is now initialized on `factory/feature/setup-001` with `https://github.com/harrycain72/software-factory.git` as `origin`. The origin is empty and parallel work remains disabled until a human:

1. creates the remote-owned initial `main` without using this local checkout for work on `main`;
2. configures branch protection to reject direct and force pushes and require pull requests, checks, and approvals;
3. records the hosting provider, pull-request command/API, required gates, commit-preserving merge strategy, branch retention, and actual project commands in `factory/repo.md`;
4. delivers these bootstrap files through a factory feature branch, release branch, and pull request;
5. verifies every configured provider model and role, then runs the contract tests serially before a two-worker exercise.

Do not initialize a disposable `origin/main` merely to make preflight green; connect this factory to the repository it is meant to govern.

## Maintenance

Edit canonical Claude role bodies or `factory/runtime-models.json`, then run:

```sh
python3 factory/render-runtime-adapters.py
python3 factory/render-runtime-adapters.py --check
```

Never hand-edit `.codex/agents/` or `.github/agents/`.
