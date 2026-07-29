#!/usr/bin/env python3
"""Validate the public X-methodology Skill contract without private sources."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = (
    REPO_ROOT / "plugins" / "mileswang-skill" / "skills" / "miles-x-methodology"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_LABELS = {
    "来源明确", "事实摘要", "AI 推断", "未核验主张", "Miles 可迁移行动"
}
EXPECTED_SECTIONS = {
    "博主说了什么事", "博主回答了什么问题", "第一性原理", "方法论",
    "Miles 可以迁移什么", "不能直接相信的部分", "适用边界", "最小验证动作"
}
EXPECTED_STATES = {
    "content-present", "url-only-external-active", "url-only-acquisition-failed",
    "essential-media-missing", "single-post-no-history", "comments-requested",
    "catchy-summary-only"
}
EXPECTED_ACTIONS = {
    "analyze", "acquire-then-analyze", "stop", "lower-conclusion",
    "analyze-with-boundary", "confirm-scope-expansion", "reject"
}
EXPECTED_SOURCE_ROLES = {
    "protected-positive-baseline", "acceptance-record",
    "protected-negative-baseline", "confirmed-requirements"
}


class XMethodologyContractError(Exception):
    pass


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise XMethodologyContractError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise XMethodologyContractError(f"expected JSON object at {path}")
    return value


def validate_source_manifest(skill_root: Path = SKILL_ROOT) -> list[str]:
    path = skill_root / "references" / "source-manifest.json"
    payload = read_json(path)
    if set(payload) != {"schema_version", "sources"}:
        raise XMethodologyContractError("source manifest has unexpected keys")
    if payload["schema_version"] != 1:
        raise XMethodologyContractError("source manifest schema_version must be 1")
    sources = payload["sources"]
    if not isinstance(sources, list) or not sources:
        raise XMethodologyContractError("source manifest must be non-empty")

    ids: set[str] = set()
    roles: set[str] = set()
    for source in sources:
        expected_keys = {"id", "role", "confirmation", "sha256", "distribution"}
        if not isinstance(source, dict) or set(source) != expected_keys:
            raise XMethodologyContractError("source entry has unexpected keys")
        source_id = source["id"]
        if not isinstance(source_id, str) or not source_id:
            raise XMethodologyContractError("source id must be non-empty")
        if source_id in ids:
            raise XMethodologyContractError(f"duplicate source id: {source_id}")
        ids.add(source_id)
        roles.add(source["role"])
        if not SHA256_RE.fullmatch(source["sha256"]):
            raise XMethodologyContractError(f"invalid SHA-256 for {source_id}")
        if source["distribution"] != "local-only":
            raise XMethodologyContractError(
                f"private source {source_id} must remain local-only"
            )
        if not str(source["confirmation"]).startswith("user-"):
            raise XMethodologyContractError(
                f"source {source_id} lacks explicit user confirmation state"
            )
    if roles != EXPECTED_SOURCE_ROLES:
        raise XMethodologyContractError("source manifest roles are incomplete")
    return [f"{len(sources)} local-only source identities", "positive and negative baselines"]


def validate_behavior_cases(repo_root: Path = REPO_ROOT) -> list[str]:
    payload = read_json(repo_root / "tests" / "x-methodology-cases.json")
    if set(payload) != {"schema_version", "required_labels", "required_sections", "cases"}:
        raise XMethodologyContractError("X methodology cases have unexpected keys")
    if payload["schema_version"] != 1:
        raise XMethodologyContractError("X methodology cases schema_version must be 1")
    if set(payload["required_labels"]) != EXPECTED_LABELS:
        raise XMethodologyContractError("X methodology evidence labels are incomplete")
    if set(payload["required_sections"]) != EXPECTED_SECTIONS:
        raise XMethodologyContractError("X methodology report sections are incomplete")
    cases = payload["cases"]
    if not isinstance(cases, list) or not cases:
        raise XMethodologyContractError("X methodology cases must be non-empty")

    ids: set[str] = set()
    states: set[str] = set()
    actions: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or set(case) != {
            "id", "input_state", "expected_action", "must_show"
        }:
            raise XMethodologyContractError("X methodology case has unexpected keys")
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id:
            raise XMethodologyContractError("X methodology case id must be non-empty")
        if case_id in ids:
            raise XMethodologyContractError(f"duplicate X methodology case: {case_id}")
        ids.add(case_id)
        states.add(case["input_state"])
        actions.add(case["expected_action"])
        must_show = case["must_show"]
        if not isinstance(must_show, list) or not must_show or not all(
            isinstance(item, str) and item for item in must_show
        ):
            raise XMethodologyContractError(f"case {case_id} needs observable assertions")
    if states != EXPECTED_STATES:
        raise XMethodologyContractError("X methodology input-state coverage is incomplete")
    if actions != EXPECTED_ACTIONS:
        raise XMethodologyContractError("X methodology action coverage is incomplete")
    return [f"{len(cases)} X methodology behavior cases", "failure and boundary coverage"]


def validate_public_skill(skill_root: Path = SKILL_ROOT) -> list[str]:
    required = {
        "SKILL.md", "references/analysis-contract.md", "references/report-template.md",
        "references/anonymous-cases.md", "references/source-manifest.json"
    }
    actual = {
        path.relative_to(skill_root).as_posix()
        for path in skill_root.rglob("*") if path.is_file()
    }
    missing = sorted(required - actual)
    if missing:
        raise XMethodologyContractError("missing public Skill files: " + ", ".join(missing))

    markdown = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(skill_root.rglob("*.md"))
    )
    for label in EXPECTED_LABELS:
        if label not in markdown:
            raise XMethodologyContractError(f"public Skill is missing label: {label}")
    for section in EXPECTED_SECTIONS:
        if section not in markdown:
            raise XMethodologyContractError(f"public Skill is missing section: {section}")
    for marker in (
        "Comments are excluded by default", "only a URL", "actually supplied and read",
        "cannot be determined", "minimum verification"
    ):
        if marker not in markdown:
            raise XMethodologyContractError(f"public Skill is missing boundary: {marker}")
    for path in skill_root.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "x.com/" in text or "twitter.com/" in text:
            raise XMethodologyContractError(
                f"public Skill must not bundle a source-post URL: {path}"
            )
    return ["public-safe X methodology files", "evidence and report markers"]


def validate_contract(repo_root: Path = REPO_ROOT) -> list[str]:
    skill_root = repo_root / "plugins" / "mileswang-skill" / "skills" / "miles-x-methodology"
    checks = validate_source_manifest(skill_root)
    checks.extend(validate_behavior_cases(repo_root))
    checks.extend(validate_public_skill(skill_root))
    return checks


def main() -> int:
    try:
        checks = validate_contract()
    except (OSError, XMethodologyContractError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    for check in checks:
        print(f"PASS: {check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
