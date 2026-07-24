#!/usr/bin/env python3
"""Reject unrouted Miles skills and fixed leaf-to-leaf chains."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTER_NAME = "mileswang"
ROUTER_MAX_LINES = 180
CROSS_SKILL_LINK_RE = re.compile(r"\.\./([a-z0-9-]+)/SKILL\.md")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class RoutingContractError(Exception):
    pass


def read_contract(path: Path) -> tuple[list[dict], set[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RoutingContractError(f"invalid routing cases at {path}: {exc}") from exc

    cases = payload.get("cases") if isinstance(payload, dict) else None
    if not isinstance(cases, list) or not cases:
        raise RoutingContractError("routing-cases.json must contain a non-empty cases list")
    external = payload.get("external_skills", [])
    if not isinstance(external, list) or not all(
        isinstance(name, str) and SKILL_NAME_RE.fullmatch(name) for name in external
    ):
        raise RoutingContractError(
            "routing-cases.json external_skills must be unique kebab-case names"
        )
    if len(external) != len(set(external)):
        raise RoutingContractError("routing-cases.json has duplicate external_skills")
    return cases, set(external)


def validate_routing_contract(repo_root: Path = REPO_ROOT) -> list[str]:
    skills_root = repo_root / "plugins" / "mileswang-skill" / "skills"
    router_path = skills_root / ROUTER_NAME / "SKILL.md"
    readme_path = repo_root / "README.md"
    cases_path = repo_root / "tests" / "routing-cases.json"

    if not router_path.is_file():
        raise RoutingContractError(f"missing router: {router_path}")

    skill_names = {
        path.parent.name for path in skills_root.glob("*/SKILL.md") if path.is_file()
    }
    if ROUTER_NAME not in skill_names:
        raise RoutingContractError(f"{ROUTER_NAME} is not a discovered skill")
    leaf_names = skill_names - {ROUTER_NAME}
    if not leaf_names:
        raise RoutingContractError("the plugin must contain at least one leaf skill")

    router_text = router_path.read_text(encoding="utf-8")
    router_lines = len(router_text.splitlines())
    if router_lines > ROUTER_MAX_LINES:
        raise RoutingContractError(
            f"router has {router_lines} lines; thin-router ceiling is {ROUTER_MAX_LINES}"
        )

    readme = readme_path.read_text(encoding="utf-8")
    errors: list[str] = []
    for name in sorted(leaf_names):
        expected_link = f"../{name}/SKILL.md"
        if expected_link not in router_text:
            errors.append(f"router does not link leaf skill {name}")
        if f"`{name}`" not in readme:
            errors.append(f"README does not document leaf skill {name}")

        leaf_path = skills_root / name / "SKILL.md"
        leaf_text = leaf_path.read_text(encoding="utf-8")
        direct_targets = set(CROSS_SKILL_LINK_RE.findall(leaf_text)) - {
            ROUTER_NAME,
            name,
        }
        direct_leaf_targets = sorted(direct_targets & leaf_names)
        if direct_leaf_targets:
            errors.append(
                f"leaf skill {name} links directly to leaf skill(s): "
                + ", ".join(direct_leaf_targets)
            )

    cases, external_skills = read_contract(cases_path)
    overlap = sorted(external_skills & skill_names)
    if overlap:
        errors.append(
            "external_skills must not duplicate bundled skills: " + ", ".join(overlap)
        )

    case_ids: set[str] = set()
    covered_leaves: set[str] = set()
    used_external_skills: set[str] = set()
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            errors.append(f"routing case {index} must be an object")
            continue
        case_id = case.get("id")
        request = case.get("request")
        expected = case.get("expected_skill")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"routing case {index} has no non-empty id")
        elif case_id in case_ids:
            errors.append(f"duplicate routing case id: {case_id}")
        else:
            case_ids.add(case_id)
        if not isinstance(request, str) or not request.strip():
            errors.append(f"routing case {case_id or index} has no request")
        if not isinstance(expected, str) or not expected.strip():
            errors.append(f"routing case {case_id or index} has no expected_skill")
        elif expected in leaf_names:
            covered_leaves.add(expected)
        elif expected in external_skills:
            used_external_skills.add(expected)
        elif expected != ROUTER_NAME:
            errors.append(
                f"routing case {case_id or index} targets unknown skill: {expected}"
            )

        must_show = case.get("must_show", [])
        must_not_route_to = case.get("must_not_route_to", [])
        if not isinstance(must_show, list) or not all(
            isinstance(value, str) and value.strip() for value in must_show
        ):
            errors.append(f"routing case {case_id or index} has invalid must_show")
        if not isinstance(must_not_route_to, list) or not all(
            isinstance(value, str) and value.strip() for value in must_not_route_to
        ):
            errors.append(
                f"routing case {case_id or index} has invalid must_not_route_to"
            )
        if not must_show and not must_not_route_to:
            errors.append(
                f"routing case {case_id or index} needs an observable assertion"
            )

    uncovered = sorted(leaf_names - covered_leaves)
    if uncovered:
        errors.append("leaf skills without routing cases: " + ", ".join(uncovered))
    unused_external = sorted(external_skills - used_external_skills)
    if unused_external:
        errors.append(
            "declared external skills without routing cases: "
            + ", ".join(unused_external)
        )

    if errors:
        raise RoutingContractError("\n".join(f"- {error}" for error in errors))

    return [
        f"thin router ({router_lines}/{ROUTER_MAX_LINES} lines)",
        f"{len(leaf_names)} routed and documented leaf skills",
        f"{len(cases)} routing cases with explicit external targets",
        "no direct leaf-to-leaf SKILL.md links",
    ]


def main() -> int:
    try:
        checks = validate_routing_contract()
    except RoutingContractError as exc:
        print(f"FAIL: routing contract\n{exc}", file=sys.stderr)
        return 1
    for check in checks:
        print(f"PASS: {check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
