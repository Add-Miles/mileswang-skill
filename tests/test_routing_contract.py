from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "tools" / "check_routing_contract.py"
)
SPEC = importlib.util.spec_from_file_location("check_routing_contract", MODULE_PATH)
assert SPEC and SPEC.loader
ROUTING = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ROUTING)


ROUTER_BODY = """Use [miles-one](../miles-one/SKILL.md) for one bounded task.
Read the active Skill catalog and preserve the exact canonical name.
Classify routes as `internal`, `external-available`, `unavailable`, or `ambiguous`.
Do not scan disk folders to claim availability.
Treat entries with the same canonical name as ambiguous.
A Miles layer must not rediscover or replace it.
"""

PLAYBOOK_BODY = """# Runtime route contract
Disk presence is not session availability.
Examples: pdf:pdf and github:gh-fix-ci.
Handle a duplicate canonical name explicitly.
Calling an independently installed Skill is delegation, not redistribution.
"""

LEAF_BODY = """Complete one bounded task.
Use the host-provided active Skill catalog as the only availability authority and keep the selected executor unchanged.
Do not rediscover or replace the selected executor from disk folders, plugin caches, installed inventories, or configuration files.
"""


def write_skill(root: Path, name: str, body: str) -> None:
    skill_dir = root / "plugins" / "mileswang-skill" / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")


def base_cases() -> list[dict]:
    internal = ["miles-one"]
    return [
        {
            "id": "internal",
            "request": "Do the bounded Miles task",
            "requested_skill": None,
            "active_skills": internal,
            "expected": {
                "status": "internal",
                "executor": "miles-one",
                "miles_layers": [],
                "candidates": [],
            },
            "must_show": ["bounded result"],
        },
        {
            "id": "external",
            "request": "Use `vendor:tool` for the external task",
            "requested_skill": "vendor:tool",
            "active_skills": internal + ["vendor:tool"],
            "expected": {
                "status": "external-available",
                "executor": "vendor:tool",
                "miles_layers": [],
                "candidates": [],
            },
            "must_show": ["vendor:tool"],
        },
        {
            "id": "unavailable-cache",
            "request": "Use `vendor:cached` from disk",
            "requested_skill": "vendor:cached",
            "active_skills": internal,
            "inactive_skills": ["vendor:cached"],
            "expected": {
                "status": "unavailable",
                "executor": None,
                "miles_layers": [],
                "candidates": [],
            },
            "must_show": ["unavailable"],
            "must_not_route_to": ["vendor:cached"],
        },
        {
            "id": "ambiguous",
            "request": "Choose between two equal external tools",
            "requested_skill": None,
            "active_skills": internal + ["vendor:one", "vendor:two"],
            "expected": {
                "status": "ambiguous",
                "executor": None,
                "miles_layers": [],
                "candidates": ["vendor:one", "vendor:two"],
            },
            "must_show": ["one question"],
        },
        {
            "id": "explicit-mismatch",
            "request": "Use `vendor:wrong` even though vendor:right owns the task",
            "requested_skill": "vendor:wrong",
            "active_skills": internal + ["vendor:right", "vendor:wrong"],
            "expected": {
                "status": "external-available",
                "executor": "vendor:right",
                "miles_layers": ["miles-one"],
                "candidates": [],
            },
            "must_show": ["task fit"],
            "must_not_route_to": ["vendor:wrong"],
        },
        {
            "id": "duplicate-canonical-name",
            "request": "Use `vendor:collision` for this task",
            "requested_skill": "vendor:collision",
            "active_skills": internal
            + ["vendor:collision", "vendor:collision"],
            "expected": {
                "status": "ambiguous",
                "executor": None,
                "miles_layers": [],
                "candidates": ["vendor:collision"],
            },
            "must_show": ["duplicate canonical name"],
            "must_not_route_to": ["vendor:collision"],
        },
    ]


def write_fixture(root: Path, include_orphan: bool = False) -> None:
    write_skill(root, "mileswang", ROUTER_BODY)
    write_skill(root, "miles-one", LEAF_BODY)
    if include_orphan:
        write_skill(root, "miles-orphan", "I am not registered.\n")

    playbook = (
        root
        / "plugins"
        / "mileswang-skill"
        / "skills"
        / "mileswang"
        / "references"
        / "routing-playbook.md"
    )
    playbook.parent.mkdir(parents=True, exist_ok=True)
    playbook.write_text(PLAYBOOK_BODY, encoding="utf-8")

    (root / "README.md").write_text("`miles-one`\n", encoding="utf-8")
    cases_dir = root / "tests"
    cases_dir.mkdir(parents=True, exist_ok=True)
    (cases_dir / "routing-cases.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "internal_skills": ["miles-one"],
                "cases": base_cases(),
            }
        ),
        encoding="utf-8",
    )


def read_fixture_contract(root: Path) -> tuple[Path, dict]:
    path = root / "tests" / "routing-cases.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


class RoutingContractTests(unittest.TestCase):
    def test_current_repository_contract_passes(self) -> None:
        checks = ROUTING.validate_routing_contract()
        self.assertTrue(any("runtime cases" in check for check in checks))

    def test_rejects_unrouted_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root, include_orphan=True)
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "router does not link leaf Skill miles-orphan",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_direct_leaf_to_leaf_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            write_skill(
                root,
                "miles-two",
                "Continue with [miles-one](../miles-one/SKILL.md).\n",
            )
            router = (
                root
                / "plugins"
                / "mileswang-skill"
                / "skills"
                / "mileswang"
                / "SKILL.md"
            )
            router.write_text(
                router.read_text(encoding="utf-8")
                + "Use [miles-two](../miles-two/SKILL.md).\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "`miles-one` and `miles-two`\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "leaf Skill miles-two links directly to leaf Skill",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_duplicate_case_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            path, payload = read_fixture_contract(root)
            payload["cases"].append(dict(payload["cases"][0]))
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError, "duplicate routing case id: internal"
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_external_executor_not_in_active_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            path, payload = read_fixture_contract(root)
            external = payload["cases"][1]
            external["expected"]["executor"] = "vendor:absent"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError, "external executor must be active"
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_active_skill_marked_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            path, payload = read_fixture_contract(root)
            unavailable = payload["cases"][2]
            unavailable["request"] = "Use `vendor:tool`"
            unavailable["requested_skill"] = "vendor:tool"
            unavailable["active_skills"].append("vendor:tool")
            unavailable["inactive_skills"] = []
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "marks an active requested Skill unavailable",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_inactive_requested_skill_replaced_by_external(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            path, payload = read_fixture_contract(root)
            unavailable = payload["cases"][2]
            unavailable["active_skills"].append("vendor:substitute")
            unavailable["expected"] = {
                "status": "external-available",
                "executor": "vendor:substitute",
                "miles_layers": [],
                "candidates": [],
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "must mark an inactive explicitly requested Skill unavailable",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_inactive_requested_skill_replaced_by_internal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            path, payload = read_fixture_contract(root)
            unavailable = payload["cases"][2]
            unavailable["expected"] = {
                "status": "internal",
                "executor": "miles-one",
                "miles_layers": [],
                "candidates": [],
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "must mark an inactive explicitly requested Skill unavailable",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_omitted_requested_skill_field(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            path, payload = read_fixture_contract(root)
            internal = payload["cases"][0]
            internal["request"] = "Use `vendor:missing` for this task"
            del internal["requested_skill"]
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "missing required keys: requested_skill",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_explicit_name_with_null_requested_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            path, payload = read_fixture_contract(root)
            internal = payload["cases"][0]
            internal["request"] = "Use `vendor:missing` for this task"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "explicitly names Skill.*requested_skill is null",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_ambiguous_route_with_one_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            path, payload = read_fixture_contract(root)
            payload["cases"][3]["expected"]["candidates"] = ["vendor:one"]
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "ambiguous route needs two candidates",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_non_ambiguous_duplicate_canonical_executor(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            path, payload = read_fixture_contract(root)
            external = payload["cases"][1]
            external["active_skills"].append("vendor:tool")
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "selects an executor with a duplicate canonical name",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_leaf_without_router_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            write_skill(root, "miles-one", "Complete one bounded task.\n")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "leaf Skill miles-one is missing router-boundary marker",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_installed_state_selection_in_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            playbook = (
                root
                / "plugins"
                / "mileswang-skill"
                / "skills"
                / "mileswang"
                / "references"
                / "routing-playbook.md"
            )
            playbook.write_text(
                playbook.read_text(encoding="utf-8")
                + "\nSelect the installed browser Skill as executor.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "selects an executor from installed-state wording",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_disk_skill_discovery_in_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            leaf = (
                root
                / "plugins"
                / "mileswang-skill"
                / "skills"
                / "miles-one"
                / "SKILL.md"
            )
            leaf.write_text(
                leaf.read_text(encoding="utf-8")
                + "\nScan ~/.codex/skills to discover an executor.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "uses disk/cache discovery as availability evidence",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_leaf_executor_reselection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            leaf = (
                root
                / "plugins"
                / "mileswang-skill"
                / "skills"
                / "miles-one"
                / "SKILL.md"
            )
            leaf.write_text(
                leaf.read_text(encoding="utf-8")
                + "\nWhen invoked, select a new executor from the active Skill catalog.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "leaf Skill miles-one attempts to reselect the executor",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_template_without_active_catalog_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            template = root / "templates" / "AGENTS.md"
            template.parent.mkdir(parents=True, exist_ok=True)
            template.write_text(
                "Check installed skills before acting.\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "templates/AGENTS.md is missing routing marker",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_malformed_namespaced_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            path, payload = read_fixture_contract(root)
            payload["cases"][1]["active_skills"].append("vendor::broken")
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError, "invalid canonical Skill name"
            ):
                ROUTING.validate_routing_contract(root)


if __name__ == "__main__":
    unittest.main()
