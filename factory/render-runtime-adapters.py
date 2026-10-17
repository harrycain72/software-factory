#!/usr/bin/env python3
"""Render runtime-specific agent profiles from canonical Claude role files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Dict, Iterable, Mapping, Tuple


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory" / "runtime-models.json"
CLAUDE_DIR = ROOT / ".claude" / "agents"
CODEX_DIR = ROOT / ".codex" / "agents"
COPILOT_DIR = ROOT / ".github" / "agents"
CODEX_CONFIG = ROOT / ".codex" / "config.toml"
SKILL_LINK = ROOT / ".agents" / "skills" / "factory"

ROLES = (
    "spec-writer",
    "builder",
    "reviewer-security",
    "reviewer-ux",
    "reviewer-ui",
    "reviewer-code",
    "approver",
)
PROVIDERS = ("claude", "codex", "github-copilot")
REQUIRED_META = ("name", "description", "tools", "model")


class ConfigurationError(ValueError):
    pass


def load_manifest() -> Mapping[str, object]:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"invalid manifest: {exc}") from exc
    if set(data) != {"defaults", "overrides"}:
        raise ConfigurationError("manifest must contain only defaults and overrides")
    defaults = data["defaults"]
    overrides = data["overrides"]
    if not isinstance(defaults, dict) or set(defaults) != set(PROVIDERS):
        raise ConfigurationError("manifest defaults must define every provider exactly once")
    if not isinstance(overrides, dict):
        raise ConfigurationError("manifest overrides must be an object")
    for provider, model in defaults.items():
        if not isinstance(model, str) or not model.strip():
            raise ConfigurationError(f"invalid default model for {provider}")
    for role, values in overrides.items():
        if role not in ROLES or not isinstance(values, dict):
            raise ConfigurationError(f"invalid override role: {role}")
        if not set(values).issubset(PROVIDERS):
            raise ConfigurationError(f"invalid provider override for {role}")
        for provider, model in values.items():
            if not isinstance(model, str) or not model.strip():
                raise ConfigurationError(f"invalid model for {role}/{provider}")
    return data


def resolved_model(manifest: Mapping[str, object], role: str, provider: str) -> str:
    defaults = manifest["defaults"]
    overrides = manifest["overrides"]
    assert isinstance(defaults, dict) and isinstance(overrides, dict)
    role_overrides = overrides.get(role, {})
    assert isinstance(role_overrides, dict)
    return str(role_overrides.get(provider, defaults[provider]))


def parse_canonical(path: Path) -> Tuple[Dict[str, str], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ConfigurationError(f"missing canonical role {path}: {exc}") from exc
    if not raw.startswith(b"---\n"):
        raise ConfigurationError(f"{path}: missing YAML frontmatter")
    marker = raw.find(b"\n---\n", 4)
    if marker < 0:
        raise ConfigurationError(f"{path}: unterminated YAML frontmatter")
    front = raw[4:marker].decode("utf-8")
    body = raw[marker + 5 :]
    metadata: Dict[str, str] = {}
    for line in front.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ConfigurationError(f"{path}: unsupported frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith('"'):
            try:
                decoded = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ConfigurationError(f"{path}: invalid quoted scalar for {key}") from exc
            if not isinstance(decoded, str):
                raise ConfigurationError(f"{path}: {key} must be a string")
            value = decoded
        if key in metadata:
            raise ConfigurationError(f"{path}: duplicate frontmatter key {key}")
        metadata[key] = value
    if set(metadata) != set(REQUIRED_META):
        raise ConfigurationError(f"{path}: frontmatter keys must be {', '.join(REQUIRED_META)}")
    return metadata, body


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def claude_profile(role: str, meta: Mapping[str, str], body: bytes, model: str) -> bytes:
    front = (
        "---\n"
        f"name: {yaml_scalar(role)}\n"
        f"description: {yaml_scalar(meta['description'])}\n"
        f"tools: {yaml_scalar(meta['tools'])}\n"
        f"model: {yaml_scalar(model)}\n"
        "---\n"
    ).encode("utf-8")
    return front + body


def body_digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def codex_profile(role: str, meta: Mapping[str, str], model: str, body: bytes) -> bytes:
    instruction = (
        f"Read .claude/agents/{role}.md. Ignore that file's YAML frontmatter and "
        "follow its Markdown body as the complete role contract. "
        f"Expected canonical Markdown body SHA-256: {body_digest(body)}."
    )
    text = (
        f"name = {json.dumps(role)}\n"
        f"description = {json.dumps(meta['description'])}\n"
        f"model = {json.dumps(model)}\n"
        f"developer_instructions = {json.dumps(instruction)}\n"
    )
    return text.encode("utf-8")


def copilot_profile(role: str, meta: Mapping[str, str], model: str, body_bytes: bytes) -> bytes:
    body = (
        f"Read `.claude/agents/{role}.md`, ignore its YAML frontmatter, and follow "
        "its Markdown body as the complete role contract. "
        f"Expected canonical Markdown body SHA-256: `{body_digest(body_bytes)}`.\n"
    )
    front = (
        "---\n"
        f"name: {yaml_scalar(role)}\n"
        f"description: {yaml_scalar(meta['description'])}\n"
        f"tools: {yaml_scalar(meta['tools'])}\n"
        "include-custom-instructions: true\n"
        f"model: {yaml_scalar(model)}\n"
        "---\n"
    )
    return (front + body).encode("utf-8")


def expected_outputs() -> Dict[Path, bytes]:
    manifest = load_manifest()
    if not CLAUDE_DIR.is_dir():
        raise ConfigurationError(f"missing canonical role directory: {CLAUDE_DIR}")
    discovered = {path.stem for path in CLAUDE_DIR.glob("*.md")}
    if discovered != set(ROLES):
        missing = sorted(set(ROLES) - discovered)
        unknown = sorted(discovered - set(ROLES))
        raise ConfigurationError(f"canonical roles differ; missing={missing}, unknown={unknown}")

    outputs: Dict[Path, bytes] = {}
    for role in ROLES:
        source = CLAUDE_DIR / f"{role}.md"
        meta, body = parse_canonical(source)
        if meta["name"] != role:
            raise ConfigurationError(f"{source}: name does not match filename")
        outputs[source] = claude_profile(
            role, meta, body, resolved_model(manifest, role, "claude")
        )
        outputs[CODEX_DIR / f"{role}.toml"] = codex_profile(
            role, meta, resolved_model(manifest, role, "codex"), body
        )
        outputs[COPILOT_DIR / f"{role}.agent.md"] = copilot_profile(
            role, meta, resolved_model(manifest, role, "github-copilot"), body
        )
    return outputs


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            os.fchmod(handle.fileno(), 0o644)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temp_path), str(path))
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def validate_static_entrypoints() -> Iterable[str]:
    try:
        config_lines = [
            line.strip()
            for line in CODEX_CONFIG.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if config_lines != ["[agents]", "enabled = true"]:
            yield f"stale or invalid {CODEX_CONFIG.relative_to(ROOT)}"
    except OSError:
        yield f"missing {CODEX_CONFIG.relative_to(ROOT)}"

    expected_target = Path("../../.claude/skills/factory")
    if SKILL_LINK.is_symlink():
        if Path(os.readlink(str(SKILL_LINK))) != expected_target:
            yield f"wrong skill symlink target: {os.readlink(str(SKILL_LINK))}"
    elif SKILL_LINK.is_dir():
        canonical = ROOT / ".claude" / "skills" / "factory"
        canonical_files = {
            path.relative_to(canonical): path.read_bytes()
            for path in canonical.rglob("*")
            if path.is_file()
        }
        adapter_files = {
            path.relative_to(SKILL_LINK): path.read_bytes()
            for path in SKILL_LINK.rglob("*")
            if path.is_file()
        }
        if canonical_files != adapter_files:
            yield "copied factory skill differs from canonical directory"
    else:
        yield "missing .agents/skills/factory entrypoint"


def check(outputs: Mapping[Path, bytes]) -> int:
    problems = list(validate_static_entrypoints())
    for path, expected in outputs.items():
        try:
            actual = path.read_bytes()
        except OSError:
            problems.append(f"missing {path.relative_to(ROOT)}")
            continue
        if actual != expected:
            problems.append(f"stale {path.relative_to(ROOT)}")
    expected_codex = {path for path in outputs if path.parent == CODEX_DIR}
    expected_copilot = {path for path in outputs if path.parent == COPILOT_DIR}
    actual_codex = set(CODEX_DIR.glob("*.toml")) if CODEX_DIR.is_dir() else set()
    actual_copilot = set(COPILOT_DIR.glob("*.agent.md")) if COPILOT_DIR.is_dir() else set()
    for path in sorted((actual_codex - expected_codex) | (actual_copilot - expected_copilot)):
        problems.append(f"unknown generated profile {path.relative_to(ROOT)}")
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    args = parser.parse_args()
    try:
        outputs = expected_outputs()
        if args.check:
            return check(outputs)
        for path, content in outputs.items():
            if not path.exists() or path.read_bytes() != content:
                atomic_write(path, content)
        return check(outputs)
    except ConfigurationError as exc:
        print(f"adapter renderer: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
