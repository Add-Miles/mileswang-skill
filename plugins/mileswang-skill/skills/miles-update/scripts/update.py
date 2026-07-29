#!/usr/bin/env python3
"""Update only the official mileswang-skill to the latest stable release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


PLUGIN_ID = "mileswang-skill@mileswang-skill"
MARKETPLACE = "mileswang-skill"
REPOSITORY = "Add-Miles/mileswang-skill"
REPOSITORY_URL = f"https://github.com/{REPOSITORY}.git"
RAW_MANIFEST_TEMPLATE = (
    "https://raw.githubusercontent.com/"
    f"{REPOSITORY}/{{tag}}/plugins/mileswang-skill/.codex-plugin/plugin.json"
)
RELEASE_ASSET_TEMPLATE = (
    "https://github.com/"
    f"{REPOSITORY}/releases/download/{{tag}}/{{asset}}"
)
SEMVER_RE = re.compile(r"^(?:v)?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class UpdateError(RuntimeError):
    """A safe, user-reportable update failure."""


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> "Version":
        match = SEMVER_RE.fullmatch(value.strip())
        if not match:
            raise UpdateError("version is not a stable semantic version")
        return cls(*(int(group) for group in match.groups()))

    @property
    def text(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def tag(self) -> str:
        return f"v{self.text}"


@dataclass(frozen=True)
class Release:
    version: Version
    tag: str
    asset_name: str
    asset_digest: str


@dataclass(frozen=True)
class Installation:
    version: Version
    source: str
    other_plugins: dict[str, tuple[str, bool]]


Runner = Callable[[list[str]], dict[str, Any]]
ByteFetcher = Callable[[str], bytes]
TagLister = Callable[[], list[Version]]


def fetch_bytes(url: str) -> bytes:
    raw: bytes | None = None
    curl = shutil.which("curl")
    if curl is not None:
        try:
            completed = subprocess.run(
                [
                    curl,
                    "--fail",
                    "--silent",
                    "--show-error",
                    "--location",
                    "--max-time",
                    "30",
                    "--header",
                    "User-Agent: mileswang-skill-updater",
                    url,
                ],
                check=False,
                capture_output=True,
                timeout=35,
            )
        except (OSError, subprocess.TimeoutExpired):
            completed = None
        if completed is not None and completed.returncode == 0:
            raw = completed.stdout

    if raw is not None:
        return raw

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "mileswang-skill-updater"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except (OSError, urllib.error.URLError) as exc:
        raise UpdateError("could not read the public stable-release files") from exc


def fetch_json(url: str, fetcher: ByteFetcher = fetch_bytes) -> dict[str, Any]:
    try:
        payload = json.loads(fetcher(url))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UpdateError("public stable-release metadata is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise UpdateError("public stable-release metadata has an invalid shape")
    return payload


def parse_checksum(value: bytes, expected_asset: str) -> str:
    try:
        text = value.decode("ascii")
    except UnicodeDecodeError as exc:
        raise UpdateError("stable release checksum is not ASCII") from exc
    match = re.fullmatch(rf"([0-9a-f]{{64}})  {re.escape(expected_asset)}\n?", text)
    if not match:
        raise UpdateError("stable release checksum has an invalid format")
    return match.group(1)


def build_release(
    version: Version,
    manifest: dict[str, Any],
    checksum: bytes,
    asset: bytes,
) -> Release:
    if manifest.get("name") != "mileswang-skill":
        raise UpdateError("release manifest has the wrong plugin identity")
    if manifest.get("version") != version.text:
        raise UpdateError("release tag and plugin manifest version do not match")

    expected_asset = f"mileswang-skill-v{version.text}.zip"
    expected_digest = parse_checksum(checksum, expected_asset)
    actual_digest = hashlib.sha256(asset).hexdigest()
    if actual_digest != expected_digest:
        raise UpdateError("stable release asset failed SHA-256 verification")
    return Release(version, version.tag, expected_asset, f"sha256:{actual_digest}")


def list_remote_stable_versions() -> list[Version]:
    git = shutil.which("git")
    if git is None:
        raise UpdateError("Git is unavailable")
    try:
        completed = subprocess.run(
            [git, "ls-remote", "--tags", "--refs", REPOSITORY_URL, "refs/tags/v*"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UpdateError("could not read the official stable tags") from exc
    if completed.returncode != 0:
        raise UpdateError("could not read the official stable tags")

    versions: set[Version] = set()
    for line in completed.stdout.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        match = re.fullmatch(r"refs/tags/(v\d+\.\d+\.\d+)", parts[1])
        if not match:
            continue
        try:
            version = Version.parse(match.group(1))
        except UpdateError:
            continue
        if match.group(1) == version.tag:
            versions.add(version)
    if not versions:
        raise UpdateError("official repository has no stable release tag")
    return sorted(versions)


def resolve_latest_release(
    tag_lister: TagLister = list_remote_stable_versions,
    fetcher: ByteFetcher = fetch_bytes,
) -> Release:
    versions = tag_lister()
    if not versions:
        raise UpdateError("official repository has no stable release tag")
    version = max(versions)
    tag = version.tag
    asset_name = f"mileswang-skill-v{version.text}.zip"
    manifest = fetch_json(RAW_MANIFEST_TEMPLATE.format(tag=tag), fetcher)
    asset_url = RELEASE_ASSET_TEMPLATE.format(tag=tag, asset=asset_name)
    checksum = fetcher(f"{asset_url}.sha256")
    asset = fetcher(asset_url)
    return build_release(version, manifest, checksum, asset)


def run_codex(arguments: list[str]) -> dict[str, Any]:
    if shutil.which("codex") is None:
        raise UpdateError("Codex CLI is unavailable")
    try:
        completed = subprocess.run(
            ["codex", *arguments],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UpdateError("Codex plugin command could not complete") from exc
    if completed.returncode != 0:
        raise UpdateError("Codex plugin command failed")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise UpdateError("Codex plugin command returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise UpdateError("Codex plugin command returned an invalid result")
    return payload


def inspect_installation(runner: Runner = run_codex) -> Installation:
    payload = runner(["plugin", "list", "--json"])
    installed = payload.get("installed")
    if not isinstance(installed, list):
        raise UpdateError("Codex did not report installed plugins")
    matches = [item for item in installed if isinstance(item, dict) and item.get("pluginId") == PLUGIN_ID]
    if len(matches) != 1:
        raise UpdateError("the official Miles plugin is not installed exactly once")
    item = matches[0]
    source = item.get("marketplaceSource", {}).get("source")
    if not isinstance(source, str) or normalize_source(source) != normalize_source(REPOSITORY_URL):
        raise UpdateError("the installed Miles plugin is not from the official repository")
    version_raw = item.get("version")
    if not isinstance(version_raw, str):
        raise UpdateError("the installed Miles plugin has no stable version")
    version = Version.parse(version_raw)

    others: dict[str, tuple[str, bool]] = {}
    for plugin in installed:
        if not isinstance(plugin, dict) or plugin.get("pluginId") == PLUGIN_ID:
            continue
        plugin_id = plugin.get("pluginId")
        plugin_version = plugin.get("version")
        enabled = plugin.get("enabled")
        if isinstance(plugin_id, str) and isinstance(plugin_version, str) and isinstance(enabled, bool):
            others[plugin_id] = (plugin_version, enabled)
    return Installation(version, source, others)


def normalize_source(value: str) -> str:
    normalized = value.strip().lower().removesuffix(".git").removesuffix("/")
    normalized = normalized.removeprefix("git@github.com:")
    normalized = normalized.removeprefix("ssh://git@github.com/")
    normalized = normalized.removeprefix("https://github.com/")
    normalized = normalized.removeprefix("http://github.com/")
    return normalized


def replace_marketplace(version: Version, runner: Runner) -> None:
    try:
        runner(["plugin", "marketplace", "remove", MARKETPLACE, "--json"])
    except UpdateError:
        # The prior add may have failed after removal. Treat removal as
        # idempotent; the following exact add still fails closed if a
        # conflicting marketplace remains.
        pass
    runner(
        [
            "plugin",
            "marketplace",
            "add",
            REPOSITORY,
            "--ref",
            version.tag,
            "--json",
        ]
    )
    runner(["plugin", "add", PLUGIN_ID, "--json"])


def apply_update(release: Release, runner: Runner = run_codex) -> dict[str, Any]:
    before = inspect_installation(runner)
    if release.version < before.version:
        return {"status": "local-newer", "current": before.version.text, "latest": release.version.text}
    if release.version == before.version:
        return {"status": "up-to-date", "current": before.version.text, "latest": release.version.text}

    failed_stage = "update"
    try:
        replace_marketplace(release.version, runner)
        after = inspect_installation(runner)
        if after.version != release.version:
            raise UpdateError("installed version did not match the stable release")
        if after.other_plugins != before.other_plugins:
            raise UpdateError("an unrelated plugin changed during the update")
    except UpdateError as update_error:
        failed_stage = str(update_error)
        rollback_ok = False
        try:
            replace_marketplace(before.version, runner)
            restored = inspect_installation(runner)
            rollback_ok = (
                restored.version == before.version
                and restored.other_plugins == before.other_plugins
            )
        except UpdateError:
            rollback_ok = False
        raise UpdateError(
            f"update failed; rollback {'succeeded' if rollback_ok else 'failed'}; stage: {failed_stage}"
        ) from update_error

    return {
        "status": "updated",
        "previous": before.version.text,
        "current": release.version.text,
        "restart_required": True,
    }


def check_update(release: Release, runner: Runner = run_codex) -> dict[str, Any]:
    installed = inspect_installation(runner)
    if release.version > installed.version:
        status = "update-available"
    elif release.version == installed.version:
        status = "up-to-date"
    else:
        status = "local-newer"
    return {"status": status, "current": installed.version.text, "latest": release.version.text}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "apply"))
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        release = resolve_latest_release()
        result = check_update(release) if args.action == "check" else apply_update(release)
    except UpdateError as exc:
        result = {"status": "failed", "reason": str(exc)}
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        else:
            print(f"FAILED: {result['reason']}", file=sys.stderr)
        return 1
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(result["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
