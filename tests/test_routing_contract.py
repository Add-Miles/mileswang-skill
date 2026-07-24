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


def write_skill(root: Path, name: str, body: str) -> None:
    skill_dir = root / "plugins" / "mileswang-skill" / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")


def write_fixture(root: Path, include_orphan: bool = False) -> None:
    write_skill(
        root,
        "mileswang",
        "Use [miles-one](../miles-one/SKILL.md) for one bounded task.\n",
    )
    write_skill(root, "miles-one", "Complete one bounded task.\n")
    if include_orphan:
        write_skill(root, "miles-orphan", "I am not registered.\n")
    (root / "README.md").write_text("`miles-one`\n", encoding="utf-8")
    cases_dir = root / "tests"
    cases_dir.mkdir(parents=True, exist_ok=True)
    (cases_dir / "routing-cases.json").write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "id": "one",
                        "request": "Do the bounded task",
                        "expected_skill": "miles-one",
                        "must_show": ["bounded result"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


class RoutingContractTests(unittest.TestCase):
    def test_current_repository_contract_passes(self) -> None:
        checks = ROUTING.validate_routing_contract()
        self.assertTrue(any("routed and documented" in check for check in checks))

    def test_rejects_unrouted_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root, include_orphan=True)
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError, "router does not link leaf skill miles-orphan"
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
            router_path = (
                root
                / "plugins"
                / "mileswang-skill"
                / "skills"
                / "mileswang"
                / "SKILL.md"
            )
            router_path.write_text(
                router_path.read_text(encoding="utf-8")
                + "Use [miles-two](../miles-two/SKILL.md) for task two.\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "`miles-one` and `miles-two`\n", encoding="utf-8"
            )
            cases_path = root / "tests" / "routing-cases.json"
            payload = json.loads(cases_path.read_text(encoding="utf-8"))
            payload["cases"].append(
                {
                    "id": "two",
                    "request": "Do task two",
                    "expected_skill": "miles-two",
                    "must_show": ["task two result"],
                }
            )
            cases_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "leaf skill miles-two links directly to leaf skill",
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_duplicate_case_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            cases_path = root / "tests" / "routing-cases.json"
            payload = json.loads(cases_path.read_text(encoding="utf-8"))
            payload["cases"].append(dict(payload["cases"][0]))
            cases_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError, "duplicate routing case id: one"
            ):
                ROUTING.validate_routing_contract(root)

    def test_rejects_unknown_expected_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_fixture(root)
            cases_path = root / "tests" / "routing-cases.json"
            payload = json.loads(cases_path.read_text(encoding="utf-8"))
            payload["cases"].append(
                {
                    "id": "unknown",
                    "request": "Use an ability that does not exist",
                    "expected_skill": "does-not-exist",
                    "must_show": ["impossible result"],
                }
            )
            cases_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ROUTING.RoutingContractError,
                "routing case unknown targets unknown skill: does-not-exist",
            ):
                ROUTING.validate_routing_contract(root)


if __name__ == "__main__":
    unittest.main()
