#!/usr/bin/env python3
"""Validate the public mileswang-skill package with standard-library checks."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HIGH_RISK_PATTERNS = {
    "private home path": re.compile(r"/" r"Users/[^/\s]+/"),
    "private key": re.compile(r"BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "assigned credential": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*"
        r"['\"][^<'\"\s][^'\"]{7,}['\"]"
    ),
}
PUBLISH_SCAN_ROOTS = (
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "AGENTS.md",
    "LICENSE",
    "VERSION",
    "templates",
    ".agents",
    "plugins",
    "tools",
    "tests",
)


class ValidationError(Exception):
    pass


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid JSON at {path}: {exc}") from exc


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValidationError(f"missing YAML frontmatter: {path}")
    raw, body = text[4:].split("\n---\n", 1)
    metadata: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or ":" not in line:
            raise ValidationError(f"invalid frontmatter line in {path}: {line!r}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip().strip("'\"")
        if key in metadata:
            raise ValidationError(f"duplicate frontmatter key {key!r}: {path}")
        metadata[key] = value
    if set(metadata) != {"name", "description"}:
        raise ValidationError(
            f"frontmatter must contain only name and description: {path}"
        )
    if not metadata["description"]:
        raise ValidationError(f"empty description: {path}")
    if not body.strip():
        raise ValidationError(f"empty skill body: {path}")
    return metadata, body


def validate_links(path: Path, text: str) -> None:
    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip().strip("<>").split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (path.parent / target).resolve().exists():
            raise ValidationError(f"broken local link in {path}: {raw_target}")


def iter_public_files(repo_root: Path) -> Iterable[Path]:
    for relative in PUBLISH_SCAN_ROOTS:
        candidate = repo_root / relative
        if candidate.is_file():
            yield candidate
        elif candidate.is_dir():
            for path in candidate.rglob("*"):
                if path.is_file() and ".git" not in path.parts:
                    yield path


def scan_public_files(repo_root: Path) -> None:
    for path in iter_public_files(repo_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in HIGH_RISK_PATTERNS.items():
            if pattern.search(text):
                raise ValidationError(f"{label} found in public file: {path}")


def validate_repo(repo_root: Path = REPO_ROOT) -> list[str]:
    checks: list[str] = []
    marketplace_path = repo_root / ".agents" / "plugins" / "marketplace.json"
    marketplace = read_json(marketplace_path)
    checks.append("marketplace JSON")

    if marketplace.get("name") != "mileswang-skill":
        raise ValidationError("marketplace name must be mileswang-skill")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        raise ValidationError("marketplace must expose exactly one plugin in v0.1")
    entry = entries[0]
    if entry.get("name") != "mileswang-skill":
        raise ValidationError("marketplace plugin name mismatch")
    source_path = entry.get("source", {}).get("path")
    if not isinstance(source_path, str) or not source_path.startswith("./"):
        raise ValidationError("marketplace source path must start with ./")
    plugin_dir = (repo_root / source_path).resolve()
    if not plugin_dir.is_dir():
        raise ValidationError(f"marketplace plugin path does not exist: {plugin_dir}")
    checks.append("marketplace source path")

    manifest_path = plugin_dir / ".codex-plugin" / "plugin.json"
    manifest = read_json(manifest_path)
    checks.append("plugin manifest JSON")
    if manifest.get("name") != entry.get("name"):
        raise ValidationError("plugin manifest name does not match marketplace")
    if manifest.get("license") != "MIT":
        raise ValidationError("plugin manifest license must be MIT")
    version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    if manifest.get("version") != version:
        raise ValidationError("VERSION does not match plugin manifest")

    skills_relative = manifest.get("skills")
    if not isinstance(skills_relative, str):
        raise ValidationError("plugin manifest is missing skills path")
    skills_root = (plugin_dir / skills_relative).resolve()
    if not skills_root.is_dir():
        raise ValidationError(f"plugin skills path does not exist: {skills_root}")
    required = {"mileswang", "miles-project", "miles-content"}
    discovered: set[str] = set()
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        metadata, body = parse_frontmatter(skill_file)
        name = metadata["name"]
        if not NAME_RE.fullmatch(name) or len(name) > 64:
            raise ValidationError(f"invalid skill name: {name}")
        if name != skill_file.parent.name:
            raise ValidationError(f"skill name and directory mismatch: {skill_file}")
        if "TODO" in skill_file.read_text(encoding="utf-8"):
            raise ValidationError(f"unfinished TODO in published skill: {skill_file}")
        validate_links(skill_file, body)
        discovered.add(name)
    missing = required - discovered
    if missing:
        raise ValidationError(f"required skills missing: {', '.join(sorted(missing))}")
    checks.append(f"{len(discovered)} skill folders")

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    for command in (
        "codex plugin marketplace add Add-Miles/mileswang-skill --ref main",
        "codex plugin add mileswang-skill@mileswang-skill",
    ):
        if command not in readme:
            raise ValidationError(f"README missing install command: {command}")
    checks.append("README install path")

    scan_public_files(repo_root)
    checks.append("public privacy and credential scan")
    return checks


def main() -> int:
    try:
        checks = validate_repo()
    except (OSError, ValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    for check in checks:
        print(f"PASS: {check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
