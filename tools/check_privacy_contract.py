#!/usr/bin/env python3
"""Enforce public artifact, Skill, and reachable Git-history privacy gates."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins/mileswang-skill/skills"
PRIVACY_REFERENCE = SKILLS / "mileswang/references/privacy-contract.md"
NOREPLY_RE = re.compile(r"^[^@\s]+@users\.noreply\.github\.com$")
PRIVACY_MARKERS = (
    "non-brand personal information",
    "private machine paths",
    "Agent handoff",
    "fail-closed",
)
LEAF_MARKER = "Protect Miles personal information"


class PrivacyContractError(RuntimeError):
    pass


def validate_identity_lines(lines: list[str]) -> None:
    invalid: list[str] = []
    for line in lines:
        parts = line.rstrip("\n").split("\x00")
        if len(parts) != 3:
            invalid.append("malformed identity record")
            continue
        commit, author_email, committer_email = parts
        if not NOREPLY_RE.fullmatch(author_email) or not NOREPLY_RE.fullmatch(
            committer_email
        ):
            invalid.append(commit[:12] or "unknown commit")
    if invalid:
        raise PrivacyContractError(
            "reachable Git history contains non-noreply identity metadata: "
            + ", ".join(sorted(set(invalid)))
        )


def publishable_history_refs(repo: Path = REPO) -> list[str]:
    completed = subprocess.run(
        [
            "git",
            "for-each-ref",
            "refs/heads",
            "refs/tags",
            "--format=%(refname)",
        ],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise PrivacyContractError("could not inspect publishable Git refs")
    refs = [line for line in completed.stdout.splitlines() if line]
    return ["HEAD", *refs]


def history_identity_lines(repo: Path = REPO) -> list[str]:
    refs = publishable_history_refs(repo)
    completed = subprocess.run(
        [
            "git",
            "log",
            "--format=%H%x00%ae%x00%ce",
            *refs,
        ],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise PrivacyContractError("could not inspect reachable Git history")
    return [line for line in completed.stdout.splitlines() if line]


def validate_tagger_lines(lines: list[str]) -> None:
    invalid: list[str] = []
    for line in lines:
        parts = line.rstrip("\n").split("\x00")
        if len(parts) != 3:
            invalid.append("malformed tag record")
            continue
        object_type, refname, raw_email = parts
        if object_type != "tag":
            continue
        email = raw_email.strip().removeprefix("<").removesuffix(">")
        if not NOREPLY_RE.fullmatch(email):
            invalid.append(refname or "unknown tag")
    if invalid:
        raise PrivacyContractError(
            "annotated Git tags contain non-noreply tagger metadata: "
            + ", ".join(sorted(set(invalid)))
        )


def history_tagger_lines(repo: Path = REPO) -> list[str]:
    completed = subprocess.run(
        [
            "git",
            "for-each-ref",
            "refs/tags",
            "--format=%(objecttype)%00%(refname)%00%(taggeremail)",
        ],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise PrivacyContractError("could not inspect Git tagger identities")
    return [line for line in completed.stdout.splitlines() if line]


def validate_privacy_contract(repo: Path = REPO, check_history: bool = True) -> list[str]:
    reference = (repo / PRIVACY_REFERENCE.relative_to(REPO)).read_text(
        encoding="utf-8"
    )
    errors: list[str] = []
    for marker in PRIVACY_MARKERS:
        if marker not in reference:
            errors.append(f"privacy contract missing marker: {marker}")

    skills_root = repo / SKILLS.relative_to(REPO)
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        if skill_file.parent.name == "mileswang":
            expected = "references/privacy-contract.md"
        else:
            expected = LEAF_MARKER
        if expected not in skill_file.read_text(encoding="utf-8"):
            errors.append(f"Skill lacks privacy gate: {skill_file.parent.name}")

    if errors:
        raise PrivacyContractError("\n".join(errors))
    if check_history:
        validate_identity_lines(history_identity_lines(repo))
        validate_tagger_lines(history_tagger_lines(repo))
    return [
        "public brand allowlist and protected-data boundary",
        f"privacy gate in {len(list(skills_root.glob('*/SKILL.md')))} Skills",
        "publishable commit and tag identities use GitHub noreply"
        if check_history
        else "history scan deferred",
    ]


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    skip_history = argv == ["--skip-history"]
    if argv and not skip_history:
        print("usage: check_privacy_contract.py [--skip-history]", file=sys.stderr)
        return 2
    try:
        checks = validate_privacy_contract(check_history=not skip_history)
    except (OSError, PrivacyContractError) as exc:
        print(f"FAIL: privacy contract\n{exc}", file=sys.stderr)
        return 1
    for check in checks:
        print(f"PASS: {check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
