from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_source_drift.py"
SPEC = importlib.util.spec_from_file_location("check_source_drift", MODULE_PATH)
assert SPEC and SPEC.loader
DRIFT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DRIFT)


class SourceDriftTests(unittest.TestCase):
    def write_manifest(self, root: Path, source_id: str, digest: str) -> Path:
        path = root / "manifest.json"
        path.write_text(
            json.dumps({"sources": [{"id": source_id, "sha256": digest}]}),
            encoding="utf-8",
        )
        return path

    def test_reports_unchanged_source_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.md"
            source.write_text("stable\n", encoding="utf-8")
            manifest = self.write_manifest(root, "source-one", DRIFT.sha256(source))
            report, drifted = DRIFT.build_report(
                manifest, [f"source-one={source}"], []
            )
            self.assertFalse(drifted)
            self.assertIn("UNCHANGED", report)
            self.assertEqual(source.read_text(encoding="utf-8"), "stable\n")

    def test_reports_candidate_hash_without_overwriting_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.md"
            source.write_text("candidate\n", encoding="utf-8")
            manifest = self.write_manifest(root, "source-one", "0" * 64)
            report, drifted = DRIFT.build_report(
                manifest, [f"source-one={source}"], []
            )
            self.assertTrue(drifted)
            self.assertIn("CANDIDATE_CHANGED", report)
            self.assertEqual(source.read_text(encoding="utf-8"), "candidate\n")

    def test_prints_unified_candidate_diff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stable, candidate = root / "stable.md", root / "candidate.md"
            stable.write_text("one\n", encoding="utf-8")
            candidate.write_text("two\n", encoding="utf-8")
            manifest = self.write_manifest(root, "source-one", DRIFT.sha256(stable))
            report, drifted = DRIFT.build_report(
                manifest, [], [f"{stable}={candidate}"]
            )
            self.assertTrue(drifted)
            self.assertIn("-one", report)
            self.assertIn("+two", report)

    def test_rejects_unknown_source_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.md"
            source.write_text("stable\n", encoding="utf-8")
            manifest = self.write_manifest(root, "source-one", DRIFT.sha256(source))
            with self.assertRaisesRegex(DRIFT.SourceDriftError, "unknown source id"):
                DRIFT.build_report(manifest, [f"missing={source}"], [])


if __name__ == "__main__":
    unittest.main()
