from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "build_release.py"
SPEC = importlib.util.spec_from_file_location("build_release", MODULE_PATH)
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


def write_release_fixture(root: Path) -> None:
    files = {
        ".gitignore": "PROJECT.md\ndist/\n",
        "AGENTS.md": "maintainer rules\n",
        "VERSION": "1.2.3\n",
        "README.md": "release readme\n",
        "LICENSE": "MIT\n",
        "THIRD_PARTY_NOTICES.md": "none bundled\n",
        ".agents/plugins/marketplace.json": "{}\n",
        ".github/workflows/ci.yml": "name: test\n",
        "plugins/mileswang-skill/.codex-plugin/plugin.json": "{}\n",
        "plugins/mileswang-skill/skills/mileswang/SKILL.md": "router\n",
        "templates/AGENTS.md": "portable rules\n",
        "tests/routing-cases.json": "{\"cases\": []}\n",
        "tools/validate.py": "# validator\n",
        "tools/check_routing_contract.py": "# routing contract\n",
        "tools/build_release.py": "# release builder\n",
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    (root / "PROJECT.md").write_text("private contract\n", encoding="utf-8")


class ReleaseBuildTests(unittest.TestCase):
    def test_build_is_deterministic_and_public_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_release_fixture(root)
            first = BUILD.build_release(root, root / "one")
            second = BUILD.build_release(root, root / "two")
            self.assertEqual(first.read_bytes(), second.read_bytes())

            with zipfile.ZipFile(first) as archive:
                names = archive.namelist()
            self.assertIn(
                "mileswang-skill-v1.2.3/plugins/mileswang-skill/skills/"
                "mileswang/SKILL.md",
                names,
            )
            for relative in (
                "templates/AGENTS.md",
                "tools/validate.py",
                "tools/check_routing_contract.py",
                "tools/build_release.py",
                "tests/routing-cases.json",
                ".github/workflows/ci.yml",
            ):
                with self.subTest(relative=relative):
                    self.assertIn(f"mileswang-skill-v1.2.3/{relative}", names)
            self.assertFalse(any(name.endswith("PROJECT.md") for name in names))

    def test_rejects_invalid_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_release_fixture(root)
            (root / "VERSION").write_text("latest\n", encoding="utf-8")
            with self.assertRaises(BUILD.ReleaseBuildError):
                BUILD.build_release(root, root / "dist")

    def test_rejects_non_utf8_release_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_release_fixture(root)
            hidden = root / "plugins" / "mileswang-skill" / "private.bin"
            hidden.write_bytes(b"api-key=\xff\x00private")
            with self.assertRaisesRegex(
                BUILD.ReleaseBuildError, "non-UTF-8 release input"
            ):
                BUILD.build_release(root, root / "dist")


if __name__ == "__main__":
    unittest.main()
