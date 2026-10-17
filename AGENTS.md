# Repository agent instructions

Use the canonical factory skill at `.claude/skills/factory/SKILL.md` for factory commands. Codex discovers the same skill through `.agents/skills/factory`.

Before any write, commit, ref update, push, or pull-request mutation, enforce the branch and worktree rules in `factory/repo.md`. Never work on a local `main` branch and never push directly to `main`.

Factory-owned paths are `.agents/`, `.claude/`, `.codex/`, `.github/agents/`, `factory/`, `AGENTS.md`, and `tests/test_factory_orchestration.py`. Product jobs must not modify them.
