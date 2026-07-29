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

    def test_rejects_non_utf8_public_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            hidden = root / "plugins" / "mileswang-skill" / "private.bin"
            hidden.parent.mkdir(parents=True)
            hidden.write_bytes(b"private-value=\xff\x00secret")
            with self.assertRaisesRegex(
                VALIDATE.ValidationError, "non-UTF-8 public file"
            ):
                VALIDATE.scan_public_files(root)

    def test_rejects_private_email_and_phone(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            private_email = "private" + "@" + "example.com"
            (root / "README.md").write_text(private_email, encoding="utf-8")
            with self.assertRaisesRegex(VALIDATE.ValidationError, "private email"):
                VALIDATE.scan_public_files(root)

            private_phone = "138" + "0013" + "8000"
            (root / "README.md").write_text(private_phone, encoding="utf-8")
            with self.assertRaisesRegex(VALIDATE.ValidationError, "phone number"):
                VALIDATE.scan_public_files(root)

    def test_allows_github_noreply_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            public_email = "123+Public-Brand" + "@" + "users.noreply.github.com"
            (root / "README.md").write_text(public_email, encoding="utf-8")
            VALIDATE.scan_public_files(root)

    def test_ignores_generated_python_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            cache = root / "tools" / "__pycache__" / "generated.pyc"
            cache.parent.mkdir(parents=True)
            cache.write_bytes(b"\xff\x00generated-cache")
            (root / "README.md").write_text("public source\n", encoding="utf-8")
            VALIDATE.scan_public_files(root)


class ReleaseContractTests(unittest.TestCase):
    def test_accepts_matching_version_and_pinned_readme(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            (root / "README.md").write_text(
                "--ref v1.2.3\n"
                "https://github.com/Add-Miles/mileswang-skill/releases/tag/v1.2.3\n",
                encoding="utf-8",
            )
            version = VALIDATE.validate_version_contract(root, {"version": "1.2.3"})
            self.assertEqual(version, "1.2.3")

    def test_rejects_manifest_version_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            (root / "README.md").write_text("--ref v1.2.3\n", encoding="utf-8")
            with self.assertRaises(VALIDATE.ValidationError):
                VALIDATE.validate_version_contract(root, {"version": "1.2.4"})

    def test_rejects_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with self.assertRaises(VALIDATE.ValidationError):
                VALIDATE.resolve_within(root, "../outside", "test path")


if __name__ == "__main__":
    unittest.main()
