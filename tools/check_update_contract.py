#!/usr/bin/env python3
"""Validate the self-update Skill's stable and isolated update contract."""

from __future__ import annotations

import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "plugins/mileswang-skill/skills/miles-update"


def validate_update_contract() -> list[str]:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    script = (ROOT / "scripts/update.py").read_text(encoding="utf-8")
    router = (REPO / "plugins/mileswang-skill/skills/mileswang/SKILL.md").read_text(encoding="utf-8")
    readme = (REPO / "README.md").read_text(encoding="utf-8")

    errors: list[str] = []
    for marker in (
        "latest verified stable GitHub release",
        "Never create a daemon",
        "new conversation",
        "Do not rediscover or replace the selected executor",
    ):
        if marker not in skill:
            errors.append(f"SKILL.md missing update boundary: {marker}")
    for marker in (
        "ls-remote",
        ".sha256",
        "hashlib.sha256",
        "plugin\", \"marketplace\", \"remove",
        "plugin\", \"add",
        "rollback",
        "other_plugins",
    ):
        if marker not in script:
            errors.append(f"updater missing stable-update marker: {marker}")
    forbidden = (
        "api.github.com",
        "releases/latest",
        "marketplace\", \"upgrade",
        "--ref\", \"main",
        "API_KEY",
        "Authorization",
    )
    for marker in forbidden:
        if marker in script:
            errors.append(f"updater contains forbidden behavior: {marker}")
    if "../miles-update/SKILL.md" not in router:
        errors.append("router does not link miles-update")
    if "`miles-update`" not in readme or "更新 mileswang" not in readme:
        errors.append("README does not document the update route")
    if errors:
        raise ValueError("\n".join(errors))
    return [
        "stable Git tag authority and release checksum",
        "single-plugin update and rollback boundary",
        "no background or mutable-main updater",
    ]


def main() -> int:
    try:
        checks = validate_update_contract()
    except (OSError, ValueError) as exc:
        print(f"FAIL: update contract\n{exc}", file=sys.stderr)
        return 1
    for check in checks:
        print(f"PASS: {check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
