from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "new_skill.py"
SPEC = importlib.util.spec_from_file_location("new_skill", MODULE_PATH)
assert SPEC and SPEC.loader
NEW_SKILL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NEW_SKILL)


class NewSkillTests(unittest.TestCase):
    def test_creates_valid_minimal_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            created = NEW_SKILL.create_skill(
                "miles-example",
                root,
                "Handle a bounded example when the user explicitly requests it.",
            )
            self.assertEqual(created, root / "miles-example")
            self.assertTrue((created / "references").is_dir())
            text = (created / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: miles-example", text)
            self.assertIn("description: Handle a bounded example", text)

    def test_rejects_invalid_names(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for invalid in ("Miles", "two words", "double--hyphen", "../escape", ""):
                with self.subTest(invalid=invalid):
                    with self.assertRaises(ValueError):
                        NEW_SKILL.create_skill(invalid, root, "Valid description")

    def test_refuses_to_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            NEW_SKILL.create_skill("miles-once", root, "First description")
            with self.assertRaises(FileExistsError):
                NEW_SKILL.create_skill("miles-once", root, "Second description")


if __name__ == "__main__":
    unittest.main()
