#!/usr/bin/env python3
"""Validate onboarding, navigation, and capability-state contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATES = {"released-owned", "external-runtime", "future-candidate"}
ALLOWED_MODES = {"onboarding", "post-task"}


class SystemContractError(Exception):
    pass


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemContractError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemContractError(f"expected JSON object at {path}")
    return value


def validate_capability_map(repo_root: Path) -> list[str]:
    skills_root = repo_root / "plugins" / "mileswang-skill" / "skills"
    path = skills_root / "mileswang" / "references" / "capability-map.json"
    payload = read_json(path)
    if set(payload) != {"schema_version", "capabilities"}:
        raise SystemContractError("capability map has unexpected keys")
    if payload["schema_version"] != 1:
        raise SystemContractError("capability map schema_version must be 1")
    capabilities = payload["capabilities"]
    if not isinstance(capabilities, list) or not capabilities:
        raise SystemContractError("capability map must be non-empty")

    ids: set[str] = set()
    owned_executors: set[str] = set()
    for capability in capabilities:
        if not isinstance(capability, dict) or set(capability) != {
            "id", "state", "executor", "evidence"
        }:
            raise SystemContractError("capability entry has unexpected keys")
        capability_id = capability["id"]
        state = capability["state"]
        executor = capability["executor"]
        evidence = capability["evidence"]
        if not isinstance(capability_id, str) or not capability_id:
            raise SystemContractError("capability id must be non-empty")
        if capability_id in ids:
            raise SystemContractError(f"duplicate capability id: {capability_id}")
        ids.add(capability_id)
        if state not in ALLOWED_STATES:
            raise SystemContractError(f"invalid capability state: {state}")
        if not isinstance(evidence, str) or not evidence:
            raise SystemContractError(f"missing evidence for {capability_id}")
        if state == "released-owned":
            if not isinstance(executor, str) or not executor.startswith("miles-"):
                raise SystemContractError(
                    f"released-owned capability {capability_id} needs Miles executor"
                )
            if not (skills_root / executor / "SKILL.md").is_file():
                raise SystemContractError(
                    f"released-owned executor is not bundled: {executor}"
                )
            owned_executors.add(executor)
        elif executor is not None:
            raise SystemContractError(
                f"{state} capability {capability_id} must not name an executor"
            )

    bundled_leaves = {
        path.parent.name
        for path in skills_root.glob("miles-*/SKILL.md")
        if path.parent.name != "mileswang"
    }
    if owned_executors != bundled_leaves:
        raise SystemContractError(
            "released-owned capability executors must equal bundled Miles leaves"
        )
    return [f"{len(capabilities)} capability states", "owned capability parity"]


def validate_system_cases(repo_root: Path) -> list[str]:
    path = repo_root / "tests" / "system-cases.json"
    payload = read_json(path)
    if set(payload) != {"schema_version", "cases"}:
        raise SystemContractError("system cases have unexpected keys")
    if payload["schema_version"] != 1:
        raise SystemContractError("system cases schema_version must be 1")
    cases = payload["cases"]
    if not isinstance(cases, list) or not cases:
        raise SystemContractError("system cases must be non-empty")

    ids: set[str] = set()
    modes: set[str] = set()
    post_bases: set[str] = set()
    for case in cases:
        required = {
            "id", "mode", "prior_executor", "prior_result", "user_input", "expected"
        }
        if not isinstance(case, dict) or set(case) != required:
            raise SystemContractError("system case has unexpected keys")
        case_id = case["id"]
        mode = case["mode"]
        expected = case["expected"]
        if not isinstance(case_id, str) or not case_id:
            raise SystemContractError("system case id must be non-empty")
        if case_id in ids:
            raise SystemContractError(f"duplicate system case id: {case_id}")
        ids.add(case_id)
        if mode not in ALLOWED_MODES:
            raise SystemContractError(f"invalid system mode: {mode}")
        modes.add(mode)
        if not isinstance(expected, dict):
            raise SystemContractError(f"expected must be an object: {case_id}")
        route_max = expected.get("route_count_max")
        if route_max not in {0, 1}:
            raise SystemContractError(f"route_count_max must be 0 or 1: {case_id}")
        if mode == "onboarding":
            if case["prior_executor"] is not None or case["prior_result"] is not None:
                raise SystemContractError("onboarding case cannot have a prior result")
        else:
            if not case["prior_executor"] or not case["prior_result"]:
                raise SystemContractError("post-task case requires concrete prior result")
            basis = expected.get("basis")
            if not isinstance(basis, str) or not basis:
                raise SystemContractError("post-task case requires navigation basis")
            post_bases.add(basis)

    if modes != ALLOWED_MODES:
        raise SystemContractError("system cases must cover onboarding and post-task")
    required_bases = {
        "prior-result", "explicit-next-step", "task-complete", "one-deciding-question"
    }
    if not required_bases.issubset(post_bases):
        raise SystemContractError("post-task cases are missing required navigation bases")
    return [f"{len(cases)} system behavior cases", "single-step navigation bases"]


def validate_system_contract(repo_root: Path = REPO_ROOT) -> list[str]:
    checks = validate_capability_map(repo_root)
    checks.extend(validate_system_cases(repo_root))
    router = (
        repo_root / "plugins" / "mileswang-skill" / "skills" / "mileswang" / "SKILL.md"
    ).read_text(encoding="utf-8")
    behavior = (
        repo_root
        / "plugins"
        / "mileswang-skill"
        / "skills"
        / "mileswang"
        / "references"
        / "system-behavior.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "First-use onboarding", "Pre-task routing", "Post-task navigation",
        "released-owned", "external-runtime", "future-candidate"
    ):
        if marker not in router and marker not in behavior:
            raise SystemContractError(f"system instructions missing marker: {marker}")
    checks.append("system instruction markers")
    return checks


def main() -> int:
    try:
        checks = validate_system_contract()
    except (OSError, SystemContractError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    for check in checks:
        print(f"PASS: {check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
