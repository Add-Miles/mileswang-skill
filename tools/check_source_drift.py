#!/usr/bin/env python3
"""Report private source drift without changing stable public Skill files."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    REPO_ROOT / "plugins" / "mileswang-skill" / "skills" / "miles-x-methodology"
    / "references" / "source-manifest.json"
)


class SourceDriftError(Exception):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_mapping(raw: str, label: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise SourceDriftError(f"{label} must use SOURCE_ID=PATH")
    source_id, raw_path = raw.split("=", 1)
    if not source_id or not raw_path:
        raise SourceDriftError(f"{label} must use non-empty SOURCE_ID=PATH")
    path = Path(raw_path).expanduser()
    if not path.is_file():
        raise SourceDriftError(f"{label} path is not a file: {path}")
    return source_id, path


def load_expected(manifest_path: Path) -> dict[str, str]:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceDriftError(f"invalid source manifest: {exc}") from exc
    return {source["id"]: source["sha256"] for source in payload["sources"]}


def build_report(
    manifest_path: Path,
    sources: list[str],
    comparisons: list[str],
) -> tuple[str, bool]:
    expected = load_expected(manifest_path)
    lines = ["# X Methodology Source Drift Report", ""]
    drifted = False
    for raw in sources:
        source_id, path = parse_mapping(raw, "--source")
        if source_id not in expected:
            raise SourceDriftError(f"unknown source id: {source_id}")
        actual = sha256(path)
        status = "UNCHANGED" if actual == expected[source_id] else "CANDIDATE_CHANGED"
        drifted = drifted or status != "UNCHANGED"
        lines.extend([
            f"## {source_id}", "", f"- Status: `{status}`",
            f"- Stable SHA-256: `{expected[source_id]}`",
            f"- Candidate SHA-256: `{actual}`", ""
        ])

    for raw in comparisons:
        if "=" not in raw:
            raise SourceDriftError("--compare must use STABLE_PATH=CANDIDATE_PATH")
        stable_raw, candidate_raw = raw.split("=", 1)
        stable, candidate = Path(stable_raw).expanduser(), Path(candidate_raw).expanduser()
        if not stable.is_file() or not candidate.is_file():
            raise SourceDriftError("--compare paths must both be files")
        stable_lines = stable.read_text(encoding="utf-8").splitlines()
        candidate_lines = candidate.read_text(encoding="utf-8").splitlines()
        diff = list(difflib.unified_diff(
            stable_lines, candidate_lines, fromfile="stable", tofile="candidate", lineterm=""
        ))
        lines.extend(["## Candidate content diff", "", "```diff", *diff, "```", ""])
        drifted = drifted or bool(diff)

    if not sources and not comparisons:
        raise SourceDriftError("provide at least one --source or --compare")
    lines.extend([
        "No stable Skill file was modified.",
        "A changed candidate requires Golden Sample regression and Miles approval."
    ])
    return "\n".join(lines) + "\n", drifted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--source", action="append", default=[], metavar="SOURCE_ID=PATH")
    parser.add_argument("--compare", action="append", default=[], metavar="STABLE=CANDIDATE")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report, drifted = build_report(args.manifest, args.source, args.compare)
    except (OSError, UnicodeDecodeError, SourceDriftError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
    print(report, end="")
    return 2 if drifted else 0


if __name__ == "__main__":
    raise SystemExit(main())
