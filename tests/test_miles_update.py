from __future__ import annotations

import importlib.util
import hashlib
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


def verified_release(version: str = "0.4.1", asset: bytes = b"release zip"):
    name = f"mileswang-skill-v{version}.zip"
    digest = hashlib.sha256(asset).hexdigest()
    return UPDATE.build_release(
        UPDATE.Version.parse(version),
        {"name": "mileswang-skill", "version": version},
        f"{digest}  {name}\n".encode(),
        asset,
    )


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
            if self.fail_target_add and self.pending_version == "0.4.1":
                raise UPDATE.UpdateError("simulated target add failure")
            return {"added": True}
        if args[:3] == ["plugin", "add", UPDATE.PLUGIN_ID]:
            self.version = self.pending_version
            return {"installed": True}
        raise AssertionError(f"unexpected command: {args}")


class ReleaseContractTests(unittest.TestCase):
    def test_accepts_exact_stable_release(self) -> None:
        release = verified_release()
        self.assertEqual(release.version.text, "0.4.1")
        self.assertRegex(release.asset_digest, r"^sha256:[0-9a-f]{64}$")

    def test_rejects_malformed_checksum_and_digest_mismatch(self) -> None:
        version = UPDATE.Version.parse("0.4.1")
        with self.assertRaises(UPDATE.UpdateError):
            UPDATE.build_release(
                version,
                {"name": "mileswang-skill", "version": "0.4.1"},
                b"not-a-checksum\n",
                b"release zip",
            )

        with self.assertRaises(UPDATE.UpdateError):
            UPDATE.build_release(
                version,
                {"name": "mileswang-skill", "version": "0.4.1"},
                f"{'0' * 64}  mileswang-skill-v0.4.1.zip\n".encode(),
                b"release zip",
            )

    def test_rejects_manifest_version_mismatch(self) -> None:
        with self.assertRaises(UPDATE.UpdateError):
            UPDATE.build_release(
                UPDATE.Version.parse("0.4.1"),
                {"name": "mileswang-skill", "version": "0.4.0"},
                f"{'0' * 64}  mileswang-skill-v0.4.1.zip\n".encode(),
                b"release zip",
            )

    def test_resolver_selects_highest_stable_tag_and_verifies_asset(self) -> None:
        asset = b"release zip"
        digest = hashlib.sha256(asset).hexdigest()

        def fetcher(url: str) -> bytes:
            if url.endswith("plugin.json"):
                return b'{"name":"mileswang-skill","version":"0.4.1"}'
            if url.endswith(".sha256"):
                return f"{digest}  mileswang-skill-v0.4.1.zip\n".encode()
            return asset

        release = UPDATE.resolve_latest_release(
            lambda: [UPDATE.Version.parse("0.3.0"), UPDATE.Version.parse("0.4.1")],
            fetcher,
        )
        self.assertEqual(release.version.text, "0.4.1")

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
                UPDATE.UpdateError, "public stable-release files"
            ) as raised:
                UPDATE.fetch_bytes("https://example.invalid/release.zip")
        self.assertNotIn("private network detail", str(raised.exception))

    def test_missing_git_stops_before_tag_lookup(self) -> None:
        with mock.patch.object(UPDATE.shutil, "which", return_value=None):
            with self.assertRaisesRegex(UPDATE.UpdateError, "Git is unavailable"):
                UPDATE.list_remote_stable_versions()


class UpdateBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.release = verified_release()

    def test_updates_only_official_plugin(self) -> None:
        fake = FakeCodex()
        result = UPDATE.apply_update(self.release, fake)
        self.assertEqual(result["status"], "updated")
        self.assertEqual(fake.version, "0.4.1")
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
