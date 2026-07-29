from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_x_methodology_contract.py"
SPEC = importlib.util.spec_from_file_location("check_x_methodology_contract", MODULE_PATH)
assert SPEC and SPEC.loader
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)
REPO_ROOT = Path(__file__).resolve().parents[1]


class XMethodologyContractTests(unittest.TestCase):
    def test_current_repository_contract_passes(self) -> None:
        checks = CONTRACT.validate_contract()
        self.assertIn("positive and negative baselines", checks)

    def test_rejects_public_source_url(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "miles-x-methodology"
            shutil.copytree(CONTRACT.SKILL_ROOT, root)
            examples = root / "references" / "anonymous-cases.md"
            examples.write_text(
                examples.read_text(encoding="utf-8") + "\nhttps://x.com/example/status/1\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                CONTRACT.XMethodologyContractError, "must not bundle a source-post URL"
            ):
                CONTRACT.validate_public_skill(root)

    def test_rejects_future_or_public_source_distribution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "miles-x-methodology"
            shutil.copytree(CONTRACT.SKILL_ROOT, root)
            path = root / "references" / "source-manifest.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["sources"][0]["distribution"] = "public"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                CONTRACT.XMethodologyContractError, "must remain local-only"
            ):
                CONTRACT.validate_source_manifest(root)

    def test_rejects_missing_failure_case(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "tests").mkdir()
            payload = json.loads(
                (REPO_ROOT / "tests" / "x-methodology-cases.json").read_text(encoding="utf-8")
            )
            payload["cases"] = [
                case for case in payload["cases"]
                if case["input_state"] != "url-only-acquisition-failed"
            ]
            (root / "tests" / "x-methodology-cases.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                CONTRACT.XMethodologyContractError, "input-state coverage is incomplete"
            ):
                CONTRACT.validate_behavior_cases(root)


if __name__ == "__main__":
    unittest.main()
