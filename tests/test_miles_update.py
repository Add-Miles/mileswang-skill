from __future__ import annotations

import importlib.util
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "plugins/mileswang-skill/skills/miles-update/scripts/update.py"
)
SPEC = importlib.util.spec_from_file_location("miles_update", MODULE_PATH)
assert SPEC and SPEC.loader
UPDATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = UPDATE
SPEC.loader.exec_module(UPDATE)


def release_payload(version: str = "0.4.0") -> dict:
    return {
        "draft": False,
        "prerelease": False,
        "tag_name": f"v{version}",
        "assets": [
            {
                "name": f"mileswang-skill-v{version}.zip",
                "digest": "sha256:" + "a" * 64,
            }
        ],
    }


def plugin_item(plugin_id: str, version: str, source: str, enabled: bool = True) -> dict:
    return {
        "pluginId": plugin_id,
        "version": version,
        "enabled": enabled,
        "marketplaceSource": {"source": source},
    }


class FakeCodex:
    def __init__(self, version: str = "0.3.0", fail_target_add: bool = False) -> None:
        self.version = version
        self.fail_target_add = fail_target_add
        self.pending_version = version
        self.commands: list[list[str]] = []
        self.other = plugin_item("pdf@official", "1.0.0", "local", True)

    def __call__(self, args: list[str]) -> dict:
        self.commands.append(args)
        if args == ["plugin", "list", "--json"]:
            return {
                "installed": [
                    plugin_item(
                        UPDATE.PLUGIN_ID,
                        self.version,
                        "https://github.com/Add-Miles/mileswang-skill.git",
                    ),
                    self.other,
                ]
            }
        if args[:4] == ["plugin", "marketplace", "remove", UPDATE.MARKETPLACE]:
            return {"removed": True}
        if args[:4] == ["plugin", "marketplace", "add", UPDATE.REPOSITORY]:
            self.pending_version = args[args.index("--ref") + 1].removeprefix("v")
            if self.fail_target_add and self.pending_version == "0.4.0":
                raise UPDATE.UpdateError("simulated target add failure")
            return {"added": True}
        if args[:3] == ["plugin", "add", UPDATE.PLUGIN_ID]:
            self.version = self.pending_version
            return {"installed": True}
        raise AssertionError(f"unexpected command: {args}")


class ReleaseContractTests(unittest.TestCase):
    def test_accepts_exact_stable_release(self) -> None:
        release = UPDATE.parse_release(
            release_payload(), {"name": "mileswang-skill", "version": "0.4.0"}
        )
        self.assertEqual(release.version.text, "0.4.0")

    def test_rejects_prerelease_and_missing_digest(self) -> None:
        payload = release_payload()
        payload["prerelease"] = True
        with self.assertRaises(UPDATE.UpdateError):
            UPDATE.parse_release(payload, {"name": "mileswang-skill", "version": "0.4.0"})

        payload = release_payload()
        payload["assets"][0]["digest"] = None
        with self.assertRaises(UPDATE.UpdateError):
            UPDATE.parse_release(payload, {"name": "mileswang-skill", "version": "0.4.0"})

    def test_rejects_manifest_version_mismatch(self) -> None:
        with self.assertRaises(UPDATE.UpdateError):
            UPDATE.parse_release(
                release_payload(), {"name": "mileswang-skill", "version": "0.3.0"}
            )

    def test_rejects_malformed_stable_tag(self) -> None:
        payload = release_payload()
        payload["tag_name"] = "v0.4"
        with self.assertRaises(UPDATE.UpdateError):
            UPDATE.parse_release(
                payload, {"name": "mileswang-skill", "version": "0.4.0"}
            )

    def test_network_failure_is_generic_and_fail_closed(self) -> None:
        with (
            mock.patch.object(UPDATE.shutil, "which", return_value=None),
            mock.patch.object(
                UPDATE.urllib.request,
                "urlopen",
                side_effect=urllib.error.URLError("private network detail"),
            ),
        ):
            with self.assertRaisesRegex(
                UPDATE.UpdateError, "public stable-release metadata"
            ) as raised:
                UPDATE.fetch_json(UPDATE.LATEST_RELEASE_URL)
        self.assertNotIn("private network detail", str(raised.exception))


class UpdateBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.release = UPDATE.parse_release(
            release_payload(), {"name": "mileswang-skill", "version": "0.4.0"}
        )

    def test_updates_only_official_plugin(self) -> None:
        fake = FakeCodex()
        result = UPDATE.apply_update(self.release, fake)
        self.assertEqual(result["status"], "updated")
        self.assertEqual(fake.version, "0.4.0")
        self.assertEqual(fake.other["version"], "1.0.0")
        self.assertFalse(any(command[:3] == ["plugin", "marketplace", "upgrade"] for command in fake.commands))

    def test_rolls_back_previous_stable_version(self) -> None:
        fake = FakeCodex(fail_target_add=True)
        with self.assertRaisesRegex(UPDATE.UpdateError, "rollback succeeded"):
            UPDATE.apply_update(self.release, fake)
        self.assertEqual(fake.version, "0.3.0")
        self.assertTrue(any("v0.3.0" in command for command in fake.commands))

    def test_check_does_not_mutate(self) -> None:
        fake = FakeCodex()
        result = UPDATE.check_update(self.release, fake)
        self.assertEqual(result["status"], "update-available")
        self.assertEqual(fake.commands, [["plugin", "list", "--json"]])

    def test_rejects_non_official_source(self) -> None:
        fake = FakeCodex()
        fake_source = "https://example.com/fake.git"

        def runner(args: list[str]) -> dict:
            if args == ["plugin", "list", "--json"]:
                return {"installed": [plugin_item(UPDATE.PLUGIN_ID, "0.3.0", fake_source)]}
            raise AssertionError(args)

        with self.assertRaisesRegex(UPDATE.UpdateError, "official repository"):
            UPDATE.inspect_installation(runner)

    def test_missing_codex_cli_stops_before_subprocess(self) -> None:
        with mock.patch.object(UPDATE.shutil, "which", return_value=None):
            with self.assertRaisesRegex(UPDATE.UpdateError, "Codex CLI is unavailable"):
                UPDATE.run_codex(["plugin", "list", "--json"])


if __name__ == "__main__":
    unittest.main()
