#!/usr/bin/env python3
"""Validate internal and runtime-external routing contracts."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTER_NAME = "mileswang"
ROUTER_MAX_LINES = 180
SCHEMA_VERSION = 2
ROUTE_STATUSES = {
    "internal",
    "external-available",
    "unavailable",
    "ambiguous",
}
CANONICAL_SKILL_PATTERN = (
    r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*"
    r"(?::[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)?"
)
CANONICAL_SKILL_RE = re.compile(rf"^{CANONICAL_SKILL_PATTERN}$")
BACKTICK_SKILL_RE = re.compile(rf"`({CANONICAL_SKILL_PATTERN})`")
CROSS_SKILL_LINK_RE = re.compile(r"\.\./([a-z0-9-]+)/SKILL\.md")
ROUTER_MARKERS = (
    "active Skill catalog",
    "`internal`",
    "`external-available`",
    "`unavailable`",
    "`ambiguous`",
    "exact canonical",
    "Do not scan",
    "same canonical name",
    "must not rediscover or replace it",
    "always empty for an `internal` route",
)
PLAYBOOK_MARKERS = (
    "Runtime route contract",
    "Disk presence is not session availability",
    "pdf:pdf",
    "github:gh-fix-ci",
    "duplicate canonical name",
)
LEAF_ROUTING_MARKERS = (
    "host-provided active Skill catalog",
    "keep the selected executor unchanged",
    "Do not rediscover or replace the selected executor",
)
TEMPLATE_ROUTING_MARKER = "当前会话 active Skill catalog"
UNSAFE_INSTALLED_SELECTION_RE = re.compile(
    r"\b(?:check|select|choose|use|prefer)\b[^.\n]{0,80}"
    r"\binstalled\b[^.\n]{0,80}\bskills?\b|"
    r"\bskills?\b[^.\n]{0,40}\bif one exists\b",
    re.IGNORECASE,
)
UNSAFE_DISCOVERY_RE = re.compile(
    r"^(?![^\n]*\b(?:do not|never|must not)\b)"
    r"[^\n]*\b(?:check|scan|search|inspect|read|list|enumerate|discover)\b"
    r"[^\n]{0,120}(?:\b(?:disk|filesystem|plugin caches?|cache|"
    r"local inventories?|installed skills?|installed skill (?:catalog|inventory)|"
    r"skill folders?|skill directories|configuration files?)\b|"
    r"(?:~\/)?\.(?:codex|agents|claude)\/skills)",
    re.IGNORECASE | re.MULTILINE,
)
UNSAFE_LEAF_RESELECTION_RE = re.compile(
    r"^(?![^\n]*\b(?:do not|never|must not)\b)"
    r"[^\n]*\b(?:select|choose|pick|rediscover|replace|change|switch(?:\s+to)?)\b"
    r"[^\n]{0,100}\b(?:new|another|different|selected|current|the)?\s*executor\b",
    re.IGNORECASE | re.MULTILINE,
)
CONTRACT_KEYS = {"schema_version", "internal_skills", "cases"}
CASE_KEYS = {
    "id",
    "request",
    "requested_skill",
    "active_skills",
    "inactive_skills",
    "expected",
    "must_show",
    "must_not_route_to",
}
CASE_REQUIRED_KEYS = {
    "id",
    "request",
    "requested_skill",
    "active_skills",
    "expected",
    "must_show",
}
EXPECTED_KEYS = {"status", "executor", "miles_layers", "candidates"}


class RoutingContractError(Exception):
    pass


def read_contract(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RoutingContractError(f"invalid routing cases at {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise RoutingContractError("routing-cases.json must contain an object")
    if set(payload) != CONTRACT_KEYS:
        raise RoutingContractError(
            "routing-cases.json keys must be: " + ", ".join(sorted(CONTRACT_KEYS))
        )
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise RoutingContractError(
            f"routing-cases.json schema_version must be {SCHEMA_VERSION}"
        )
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise RoutingContractError("routing-cases.json must contain non-empty cases")
    return payload


def validate_name_list(
    value: object,
    label: str,
    errors: list[str],
    *,
    allow_empty: bool = True,
    allow_duplicates: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    if not allow_empty and not value:
        errors.append(f"{label} must not be empty")

    names: list[str] = []
    for name in value:
        if not isinstance(name, str) or not CANONICAL_SKILL_RE.fullmatch(name):
            errors.append(f"{label} has invalid canonical Skill name: {name!r}")
            continue
        names.append(name)
    if not allow_duplicates and len(names) != len(set(names)):
        errors.append(f"{label} contains duplicate Skill names")
    return names


def validate_text_list(value: object, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        errors.append(f"{label} must be a list of non-empty strings")
        return []
    return value


def runtime_instruction_text(text: str) -> str:
    """Exclude quoted examples and fenced samples from imperative checks."""
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith(">"):
            continue
        lines.append(line)
    return "\n".join(lines)


def validate_routing_contract(repo_root: Path = REPO_ROOT) -> list[str]:
    skills_root = repo_root / "plugins" / "mileswang-skill" / "skills"
    router_path = skills_root / ROUTER_NAME / "SKILL.md"
    playbook_path = skills_root / ROUTER_NAME / "references" / "routing-playbook.md"
    readme_path = repo_root / "README.md"
    template_path = repo_root / "templates" / "AGENTS.md"
    cases_path = repo_root / "tests" / "routing-cases.json"

    if not router_path.is_file():
        raise RoutingContractError(f"missing router: {router_path}")
    if not playbook_path.is_file():
        raise RoutingContractError(f"missing routing playbook: {playbook_path}")

    skill_names = {
        path.parent.name for path in skills_root.glob("*/SKILL.md") if path.is_file()
    }
    if ROUTER_NAME not in skill_names:
        raise RoutingContractError(f"{ROUTER_NAME} is not a discovered Skill")
    leaf_names = skill_names - {ROUTER_NAME}
    if not leaf_names:
        raise RoutingContractError("the plugin must contain at least one leaf Skill")

    router_text = router_path.read_text(encoding="utf-8")
    router_lines = len(router_text.splitlines())
    if router_lines > ROUTER_MAX_LINES:
        raise RoutingContractError(
            f"router has {router_lines} lines; thin-router ceiling is {ROUTER_MAX_LINES}"
        )

    errors: list[str] = []
    for marker in ROUTER_MARKERS:
        if marker not in router_text:
            errors.append(f"router is missing runtime contract marker: {marker}")

    playbook_text = playbook_path.read_text(encoding="utf-8")
    for marker in PLAYBOOK_MARKERS:
        if marker not in playbook_text:
            errors.append(f"routing playbook is missing marker: {marker}")

    readme = readme_path.read_text(encoding="utf-8")
    runtime_markdown_paths = sorted(skills_root.rglob("*.md"))
    policy_markdown_paths = list(runtime_markdown_paths)
    if template_path.is_file():
        template_text = template_path.read_text(encoding="utf-8")
        if TEMPLATE_ROUTING_MARKER not in template_text:
            errors.append(
                f"templates/AGENTS.md is missing routing marker: {TEMPLATE_ROUTING_MARKER}"
            )
        policy_markdown_paths.append(template_path)
    for runtime_path in policy_markdown_paths:
        runtime_text = runtime_path.read_text(encoding="utf-8")
        instruction_text = runtime_instruction_text(runtime_text)
        forbidden = UNSAFE_INSTALLED_SELECTION_RE.search(instruction_text)
        if forbidden:
            errors.append(
                f"runtime policy document {runtime_path.relative_to(repo_root)} "
                "selects an executor from installed-state wording"
            )
        unsafe_discovery = UNSAFE_DISCOVERY_RE.search(instruction_text)
        if unsafe_discovery:
            errors.append(
                f"runtime policy document {runtime_path.relative_to(repo_root)} "
                "uses disk/cache discovery as availability evidence"
            )

    for name in sorted(leaf_names):
        expected_link = f"../{name}/SKILL.md"
        if expected_link not in router_text:
            errors.append(f"router does not link leaf Skill {name}")
        if f"`{name}`" not in readme:
            errors.append(f"README does not document leaf Skill {name}")

        leaf_path = skills_root / name / "SKILL.md"
        leaf_text = leaf_path.read_text(encoding="utf-8")
        for marker in LEAF_ROUTING_MARKERS:
            if marker not in leaf_text:
                errors.append(
                    f"leaf Skill {name} is missing router-boundary marker: {marker}"
                )
        if UNSAFE_LEAF_RESELECTION_RE.search(runtime_instruction_text(leaf_text)):
            errors.append(f"leaf Skill {name} attempts to reselect the executor")
        direct_targets = set(CROSS_SKILL_LINK_RE.findall(leaf_text)) - {
            ROUTER_NAME,
            name,
        }
        direct_leaf_targets = sorted(direct_targets & leaf_names)
        if direct_leaf_targets:
            errors.append(
                f"leaf Skill {name} links directly to leaf Skill(s): "
                + ", ".join(direct_leaf_targets)
            )

    contract = read_contract(cases_path)
    internal_skills = validate_name_list(
        contract.get("internal_skills"),
        "internal_skills",
        errors,
        allow_empty=False,
    )
    internal_set = set(internal_skills)
    if internal_set != leaf_names:
        errors.append(
            "internal_skills must exactly match bundled leaves: "
            + ", ".join(sorted(leaf_names))
        )

    case_ids: set[str] = set()
    covered_internal: set[str] = set()
    covered_statuses: set[str] = set()
    has_namespaced_external = False
    has_explicit_mismatch = False
    has_inactive_unavailable = False
    has_same_name_collision = False

    for index, case in enumerate(contract["cases"], start=1):
        label = f"routing case {index}"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        unknown_case_keys = set(case) - CASE_KEYS
        if unknown_case_keys:
            errors.append(
                f"{label} has unknown keys: " + ", ".join(sorted(unknown_case_keys))
            )
        missing_case_keys = CASE_REQUIRED_KEYS - set(case)
        if missing_case_keys:
            errors.append(
                f"{label} is missing required keys: "
                + ", ".join(sorted(missing_case_keys))
            )

        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{label} has no non-empty id")
            case_label = label
        else:
            case_label = f"routing case {case_id}"
            if case_id in case_ids:
                errors.append(f"duplicate routing case id: {case_id}")
            case_ids.add(case_id)

        request = case.get("request")
        if not isinstance(request, str) or not request.strip():
            errors.append(f"{case_label} has no request")
            mentioned_skills: set[str] = set()
        else:
            mentioned_skills = set(BACKTICK_SKILL_RE.findall(request))

        active = validate_name_list(
            case.get("active_skills"),
            f"{case_label} active_skills",
            errors,
            allow_empty=False,
            allow_duplicates=True,
        )
        inactive = validate_name_list(
            case.get("inactive_skills", []),
            f"{case_label} inactive_skills",
            errors,
        )
        active_set = set(active)
        active_counts = Counter(active)
        collision_set = {
            name for name, count in active_counts.items() if count > 1
        }
        inactive_set = set(inactive)
        overlap = sorted(active_set & inactive_set)
        if overlap:
            errors.append(
                f"{case_label} lists Skill as active and inactive: "
                + ", ".join(overlap)
            )
        missing_internal = sorted(internal_set - active_set)
        if missing_internal:
            errors.append(
                f"{case_label} active catalog is missing bundled leaves: "
                + ", ".join(missing_internal)
            )

        requested = case.get("requested_skill")
        if requested is not None:
            if not isinstance(requested, str) or not CANONICAL_SKILL_RE.fullmatch(
                requested
            ):
                errors.append(
                    f"{case_label} has invalid requested_skill: {requested!r}"
                )
                requested = None
            elif requested not in mentioned_skills:
                errors.append(
                    f"{case_label} request does not explicitly name requested_skill {requested}"
                )
        elif mentioned_skills:
            errors.append(
                f"{case_label} explicitly names Skill(s) but requested_skill is null: "
                + ", ".join(sorted(mentioned_skills))
            )

        expected = case.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{case_label} expected must be an object")
            continue
        if set(expected) != EXPECTED_KEYS:
            errors.append(
                f"{case_label} expected keys must be: "
                + ", ".join(sorted(EXPECTED_KEYS))
            )

        status = expected.get("status")
        if status not in ROUTE_STATUSES:
            errors.append(f"{case_label} has invalid status: {status!r}")
        else:
            covered_statuses.add(status)

        if requested is not None and requested not in active_set:
            if status != "unavailable":
                errors.append(
                    f"{case_label} must mark an inactive explicitly requested Skill unavailable"
                )
        if requested is not None and requested in collision_set:
            if status != "ambiguous":
                errors.append(
                    f"{case_label} must mark a duplicate canonical requested Skill ambiguous"
                )

        executor = expected.get("executor")
        if executor is not None and (
            not isinstance(executor, str)
            or not CANONICAL_SKILL_RE.fullmatch(executor)
        ):
            errors.append(f"{case_label} has invalid executor: {executor!r}")
            executor = None

        layers = validate_name_list(
            expected.get("miles_layers"),
            f"{case_label} miles_layers",
            errors,
        )
        candidates = validate_name_list(
            expected.get("candidates"),
            f"{case_label} candidates",
            errors,
        )
        layer_set = set(layers)
        candidate_set = set(candidates)

        invalid_layers = sorted(layer_set - internal_set)
        if invalid_layers:
            errors.append(
                f"{case_label} has non-Miles governance layers: "
                + ", ".join(invalid_layers)
            )
        inactive_layers = sorted(layer_set - active_set)
        if inactive_layers:
            errors.append(
                f"{case_label} uses inactive Miles layers: "
                + ", ".join(inactive_layers)
            )
        if executor in layer_set:
            errors.append(f"{case_label} repeats executor as a Miles layer")
        if executor in collision_set:
            errors.append(
                f"{case_label} selects an executor with a duplicate canonical name"
            )

        must_show = validate_text_list(
            case.get("must_show", []), f"{case_label} must_show", errors
        )
        must_not_route_to = validate_name_list(
            case.get("must_not_route_to", []),
            f"{case_label} must_not_route_to",
            errors,
        )
        if not must_show and not must_not_route_to:
            errors.append(f"{case_label} needs an observable assertion")
        if executor in set(must_not_route_to):
            errors.append(f"{case_label} forbids its expected executor")

        if status == "internal":
            if executor not in internal_set or executor not in active_set:
                errors.append(
                    f"{case_label} internal executor must be an active bundled leaf"
                )
            if layers or candidates:
                errors.append(
                    f"{case_label} internal route must not add layers or candidates"
                )
        elif status == "external-available":
            if executor is None or executor not in active_set:
                errors.append(f"{case_label} external executor must be active")
            elif executor in internal_set:
                errors.append(f"{case_label} external executor is a bundled leaf")
            elif ":" in executor:
                has_namespaced_external = True
            if candidates:
                errors.append(
                    f"{case_label} external-available route must not have candidates"
                )
        elif status == "unavailable":
            if executor is not None or layers or candidates:
                errors.append(
                    f"{case_label} unavailable route must have no executor, layers, or candidates"
                )
            if requested is None:
                errors.append(f"{case_label} unavailable route needs requested_skill")
            elif requested in active_set:
                errors.append(
                    f"{case_label} marks an active requested Skill unavailable"
                )
            if requested is not None and requested in inactive_set:
                has_inactive_unavailable = True
        elif status == "ambiguous":
            if executor is not None or layers:
                errors.append(
                    f"{case_label} ambiguous route must have no executor or layers"
                )
            collision_candidates = candidate_set & collision_set
            if len(candidate_set) < 2 and not collision_candidates:
                errors.append(
                    f"{case_label} ambiguous route needs two candidates or one duplicate canonical candidate"
                )
            inactive_candidates = sorted(candidate_set - active_set)
            if inactive_candidates:
                errors.append(
                    f"{case_label} has inactive ambiguous candidates: "
                    + ", ".join(inactive_candidates)
                )
            if collision_candidates:
                has_same_name_collision = True

        if executor in internal_set:
            covered_internal.add(executor)
        covered_internal.update(layer_set & internal_set)

        if (
            requested is not None
            and executor is not None
            and requested != executor
            and requested in active_set
            and requested in set(must_not_route_to)
        ):
            has_explicit_mismatch = True

    missing_coverage = sorted(leaf_names - covered_internal)
    if missing_coverage:
        errors.append(
            "bundled leaves without route coverage: " + ", ".join(missing_coverage)
        )
    missing_statuses = sorted(ROUTE_STATUSES - covered_statuses)
    if missing_statuses:
        errors.append("routing states without cases: " + ", ".join(missing_statuses))
    if not has_namespaced_external:
        errors.append("routing cases need a namespaced external executor")
    if not has_explicit_mismatch:
        errors.append("routing cases need an explicit-but-incompatible Skill case")
    if not has_inactive_unavailable:
        errors.append("routing cases need an inactive cache-only unavailable case")
    if not has_same_name_collision:
        errors.append("routing cases need a duplicate canonical name collision case")

    if errors:
        raise RoutingContractError("\n".join(f"- {error}" for error in errors))

    return [
        f"thin router ({router_lines}/{ROUTER_MAX_LINES} lines)",
        f"{len(leaf_names)} routed and documented bundled leaves",
        f"schema v{SCHEMA_VERSION} covers {len(contract['cases'])} runtime cases",
        "all four route states, exact canonical names, and collision handling",
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
