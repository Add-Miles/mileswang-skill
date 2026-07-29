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
SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
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
EMAIL_RE = re.compile(
    r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})(?![A-Za-z0-9.-])"
)
PUBLIC_EMAIL_RE = re.compile(r"^[^@\s]+@users\.noreply\.github\.com$")
PUBLIC_PROTOCOL_IDENTITIES = {"git@github.com"}
PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
IGNORED_PUBLIC_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".DS_Store",
    "build",
    "dist",
}
LOCAL_ONLY_FILES = {"PROJECT.md"}


class ValidationError(Exception):
    pass


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid JSON at {path}: {exc}") from exc


def resolve_within(base: Path, relative: str, label: str) -> Path:
    resolved_base = base.resolve()
    resolved = (resolved_base / relative).resolve()
    try:
        resolved.relative_to(resolved_base)
    except ValueError as exc:
        raise ValidationError(f"{label} escapes its allowed directory: {relative}") from exc
    return resolved


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
    for path in repo_root.rglob("*"):
        relative = path.relative_to(repo_root)
        if relative.as_posix() in LOCAL_ONLY_FILES:
            continue
        if set(relative.parts) & IGNORED_PUBLIC_PARTS:
            continue
        if path.is_file():
            yield path


def scan_public_files(repo_root: Path) -> None:
    for path in iter_public_files(repo_root):
        if path.is_symlink():
            raise ValidationError(f"symlink is not allowed in public files: {path}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(
                f"non-UTF-8 public file requires an explicit release policy: {path}"
            ) from exc
        for label, pattern in HIGH_RISK_PATTERNS.items():
            if pattern.search(text):
                raise ValidationError(f"{label} found in public file: {path}")
        for match in EMAIL_RE.finditer(text):
            value = match.group(1)
            if value not in PUBLIC_PROTOCOL_IDENTITIES and not PUBLIC_EMAIL_RE.fullmatch(value):
                raise ValidationError(f"private email found in public file: {path}")
        if PHONE_RE.search(text):
            raise ValidationError(f"phone number found in public file: {path}")


def validate_all_json(repo_root: Path) -> int:
    json_paths = sorted(
        path for path in iter_public_files(repo_root) if path.suffix == ".json"
    )
    for path in json_paths:
        read_json(path)
    return len(json_paths)


def validate_version_contract(repo_root: Path, manifest: dict) -> str:
    version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER_RE.fullmatch(version):
        raise ValidationError(
            f"VERSION must be stable semantic version x.y.z: {version!r}"
        )
    if manifest.get("version") != version:
        raise ValidationError("VERSION does not match plugin manifest")

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    release_ref = f"--ref v{version}"
    if release_ref not in readme:
        raise ValidationError(f"README stable install command must pin {release_ref}")
    release_url = (
        "https://github.com/Add-Miles/mileswang-skill/releases/tag/" f"v{version}"
    )
    if release_url not in readme:
        raise ValidationError(f"README current release link must point to v{version}")
    return version


def validate_repo(repo_root: Path = REPO_ROOT) -> list[str]:
    checks: list[str] = []
    json_count = validate_all_json(repo_root)
    checks.append(f"{json_count} public JSON files")

    marketplace_path = repo_root / ".agents" / "plugins" / "marketplace.json"
    marketplace = read_json(marketplace_path)

    if marketplace.get("name") != "mileswang-skill":
        raise ValidationError("marketplace name must be mileswang-skill")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        raise ValidationError("marketplace must expose exactly one plugin")
    entry = entries[0]
    if entry.get("name") != "mileswang-skill":
        raise ValidationError("marketplace plugin name mismatch")
    source_path = entry.get("source", {}).get("path")
    if not isinstance(source_path, str) or not source_path.startswith("./"):
        raise ValidationError("marketplace source path must start with ./")
    plugin_dir = resolve_within(repo_root, source_path, "marketplace plugin path")
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
    version = validate_version_contract(repo_root, manifest)
    checks.append(f"release version contract v{version}")

    skills_relative = manifest.get("skills")
    if not isinstance(skills_relative, str):
        raise ValidationError("plugin manifest is missing skills path")
    skills_root = resolve_within(plugin_dir, skills_relative, "plugin skills path")
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
        f"codex plugin marketplace add Add-Miles/mileswang-skill --ref v{version}",
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
