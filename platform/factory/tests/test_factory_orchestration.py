from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FACTORY = ROOT / "factory"
ROLES = (
    "spec-writer",
    "builder",
    "reviewer-security",
    "reviewer-ux",
    "reviewer-ui",
    "reviewer-code",
    "approver",
)


def run(*args: str, cwd: Path = ROOT, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


class FactoryFilesTest(unittest.TestCase):
    def test_board_starts_at_schema_two(self) -> None:
        board = json.loads((FACTORY / "board.json").read_text(encoding="utf-8"))
        self.assertEqual(board, {"schema_version": 2, "active_batch": None, "jobs": []})

    def test_manifest_resolves_required_matrix(self) -> None:
        manifest = json.loads((FACTORY / "runtime-models.json").read_text(encoding="utf-8"))
        expected_defaults = {
            "claude": "sonnet",
            "codex": "gpt-5.6-terra",
            "github-copilot": "gpt-5.6-terra",
        }
        self.assertEqual(manifest["defaults"], expected_defaults)
        self.assertEqual(
            manifest["overrides"],
            {
                "reviewer-code": {
                    "claude": "opus",
                    "codex": "gpt-5.6-sol",
                    "github-copilot": "claude-opus-5.5",
                }
            },
        )

    def test_all_roles_and_generated_profiles_exist(self) -> None:
        for role in ROLES:
            self.assertTrue((ROOT / ".claude" / "agents" / f"{role}.md").is_file())
            self.assertTrue((ROOT / ".codex" / "agents" / f"{role}.toml").is_file())
            self.assertTrue((ROOT / ".github" / "agents" / f"{role}.agent.md").is_file())

    def test_codex_skill_is_canonical_symlink(self) -> None:
        link = ROOT / ".agents" / "skills" / "factory"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.readlink(), Path("../../.claude/skills/factory"))
        self.assertEqual(link.resolve(), (ROOT / ".claude" / "skills" / "factory").resolve())

    def test_renderer_check_passes(self) -> None:
        result = run("python3", "factory/render-runtime-adapters.py", "--check")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_renderer_is_deterministic_and_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            clone = Path(temp) / "repo"
            clone.mkdir()
            for relative in ("factory", ".claude", ".codex", ".github", ".agents"):
                source = ROOT / relative
                if source.exists():
                    shutil.copytree(source, clone / relative, symlinks=True)

            render = clone / "factory" / "render-runtime-adapters.py"
            first = run("python3", str(render), cwd=clone)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = {
                path.relative_to(clone): path.read_bytes()
                for parent in (clone / ".claude" / "agents", clone / ".codex" / "agents", clone / ".github" / "agents")
                for path in parent.iterdir()
                if path.is_file()
            }
            second = run("python3", str(render), cwd=clone)
            self.assertEqual(second.returncode, 0, second.stderr)
            after = {clone_path: (clone / clone_path).read_bytes() for clone_path in before}
            self.assertEqual(before, after)

            adapter = clone / ".codex" / "agents" / "builder.toml"
            adapter.write_text(adapter.read_text(encoding="utf-8") + "# drift\n", encoding="utf-8")
            drift = run("python3", str(render), "--check", cwd=clone)
            self.assertNotEqual(drift.returncode, 0)
            self.assertIn("stale .codex/agents/builder.toml", drift.stderr)

            rerender = run("python3", str(render), cwd=clone)
            self.assertEqual(rerender.returncode, 0, rerender.stderr)
            canonical = clone / ".claude" / "agents" / "builder.md"
            canonical.write_text(canonical.read_text(encoding="utf-8") + "\nNew contract line.\n", encoding="utf-8")
            body_drift = run("python3", str(render), "--check", cwd=clone)
            self.assertNotEqual(body_drift.returncode, 0)
            self.assertIn("stale .codex/agents/builder.toml", body_drift.stderr)


class BranchGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        run("git", "init", "-q", "-b", "seed", cwd=self.repo, check=True)
        run("git", "config", "user.name", "Factory Test", cwd=self.repo, check=True)
        run("git", "config", "user.email", "factory@example.invalid", cwd=self.repo, check=True)
        (self.repo / "seed.txt").write_text("seed\n", encoding="utf-8")
        run("git", "add", "seed.txt", cwd=self.repo, check=True)
        run("git", "commit", "-q", "-m", "seed", cwd=self.repo, check=True)
        run("git", "branch", "main", cwd=self.repo, check=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def guard(self, expected: str) -> subprocess.CompletedProcess[str]:
        return run("sh", str(FACTORY / "branch-guard.sh"), str(self.repo), expected, cwd=self.repo)

    def test_accepts_only_exact_non_main_branch(self) -> None:
        run("git", "switch", "-q", "-c", "factory/feature/job-001", cwd=self.repo, check=True)
        self.assertEqual(self.guard("factory/feature/job-001").returncode, 0)
        mismatch = self.guard("factory/feature/job-002")
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertIn("expected factory/feature/job-002", mismatch.stderr)

    def test_rejects_main_and_detached_head(self) -> None:
        run("git", "switch", "-q", "main", cwd=self.repo, check=True)
        on_main = self.guard("main")
        self.assertNotEqual(on_main.returncode, 0)
        self.assertIn("non-main", on_main.stderr)
        run("git", "switch", "-q", "--detach", "HEAD", cwd=self.repo, check=True)
        detached = self.guard("factory/feature/job-001")
        self.assertNotEqual(detached.returncode, 0)
        self.assertIn("detached HEAD", detached.stderr)


class IsolationScriptsTest(unittest.TestCase):
    def _copy_script(self, name: str, target: Path) -> Path:
        script = target / name
        shutil.copy2(FACTORY / name, script)
        return script

    def test_orchestrator_lock_has_one_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script = self._copy_script("orchestrator-lock.sh", Path(temp))
            self.assertEqual(run("sh", str(script), "acquire", "owner-a", cwd=Path(temp)).returncode, 0)
            occupied = run("sh", str(script), "acquire", "owner-b", cwd=Path(temp))
            self.assertNotEqual(occupied.returncode, 0)
            self.assertIn("owner-a", occupied.stderr)
            foreign = run("sh", str(script), "release", "owner-b", cwd=Path(temp))
            self.assertNotEqual(foreign.returncode, 0)
            self.assertTrue((Path(temp) / ".orchestrator-lock").is_dir())
            self.assertEqual(run("sh", str(script), "release", "owner-a", cwd=Path(temp)).returncode, 0)

    def test_slots_are_unique_and_lowercase(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script = self._copy_script("slot.sh", Path(temp))
            created = run("sh", str(script), "create", "004_builder", cwd=Path(temp))
            self.assertEqual(created.returncode, 0, created.stderr)
            self.assertEqual(created.stdout, "FACTORY_TEST_SLOT=004_builder\n")
            self.assertNotEqual(run("sh", str(script), "create", "004_builder", cwd=Path(temp)).returncode, 0)
            self.assertNotEqual(run("sh", str(script), "create", "BAD-SLOT", cwd=Path(temp)).returncode, 0)
            self.assertEqual(run("sh", str(script), "drop", "004_builder", cwd=Path(temp)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
