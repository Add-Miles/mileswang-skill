from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_system_contract.py"
SPEC = importlib.util.spec_from_file_location("check_system_contract", MODULE_PATH)
assert SPEC and SPEC.loader
SYSTEM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYSTEM)
REPO_ROOT = Path(__file__).resolve().parents[1]


class SystemContractTests(unittest.TestCase):
    def test_current_repository_contract_passes(self) -> None:
        checks = SYSTEM.validate_system_contract()
        self.assertIn("owned capability parity", checks)

    def test_future_candidate_cannot_name_executor(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = REPO_ROOT / "plugins"
            shutil.copytree(source, root / "plugins")
            path = (
                root / "plugins" / "mileswang-skill" / "skills" / "mileswang"
                / "references" / "capability-map.json"
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            future = next(
                item for item in payload["capabilities"]
                if item["state"] == "future-candidate"
            )
            future["executor"] = "miles-fake"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                SYSTEM.SystemContractError, "future-candidate.*must not name"
            ):
                SYSTEM.validate_capability_map(root)

    def test_owned_capability_must_be_bundled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = REPO_ROOT / "plugins"
            shutil.copytree(source, root / "plugins")
            path = (
                root / "plugins" / "mileswang-skill" / "skills" / "mileswang"
                / "references" / "capability-map.json"
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["capabilities"][0]["executor"] = "miles-missing"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                SYSTEM.SystemContractError, "not bundled"
            ):
                SYSTEM.validate_capability_map(root)

    def test_candidate_owned_is_not_released_owned(self) -> None:
        path = (
            REPO_ROOT / "plugins" / "mileswang-skill" / "skills" / "mileswang"
            / "references" / "capability-map.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        capability = next(
            item for item in payload["capabilities"]
            if item["executor"] == "miles-x-methodology"
        )
        self.assertEqual(capability["state"], "candidate-owned")
        self.assertIn("awaiting-real-session", capability["evidence"])

    def test_video_editing_is_released_only_with_real_acceptance(self) -> None:
        path = (
            REPO_ROOT / "plugins" / "mileswang-skill" / "skills" / "mileswang"
            / "references" / "capability-map.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        capability = next(
            item for item in payload["capabilities"]
            if item["executor"] == "miles-video-editing"
        )
        self.assertEqual(capability["state"], "released-owned")
        self.assertIn("two-real-video-renders", capability["evidence"])
        self.assertIn("clean-install", capability["evidence"])

    def test_post_task_case_requires_concrete_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "tests").mkdir()
            payload = json.loads(
                (REPO_ROOT / "tests" / "system-cases.json").read_text(encoding="utf-8")
            )
            post = next(case for case in payload["cases"] if case["mode"] == "post-task")
            post["prior_result"] = None
            (root / "tests" / "system-cases.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                SYSTEM.SystemContractError, "requires concrete prior result"
            ):
                SYSTEM.validate_system_cases(root)


if __name__ == "__main__":
    unittest.main()
