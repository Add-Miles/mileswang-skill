from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "validate.py"
SPEC = importlib.util.spec_from_file_location("validate", MODULE_PATH)
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE)


class PrivacyScanTests(unittest.TestCase):
    def test_detects_private_home_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                "private path: " + "/" + "Users" + "/example/Documents/file.md",
                encoding="utf-8",
            )
            with self.assertRaises(VALIDATE.ValidationError):
                VALIDATE.scan_public_files(root)

    def test_allows_security_guidance_without_a_secret_value(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                "Never commit an API key, token, password, or secret.", encoding="utf-8"
            )
            VALIDATE.scan_public_files(root)


if __name__ == "__main__":
    unittest.main()
