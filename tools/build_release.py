#!/usr/bin/env python3
"""Build a deterministic, public-safe mileswang-skill release bundle."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
RELEASE_PATHS = (
    Path(".gitignore"),
    Path("AGENTS.md"),
    Path("README.md"),
    Path("LICENSE"),
    Path("THIRD_PARTY_NOTICES.md"),
    Path("VERSION"),
    Path(".agents"),
    Path(".github"),
    Path("plugins/mileswang-skill"),
    Path("templates"),
    Path("tests"),
    Path("tools"),
)
IGNORED_PARTS = {"__pycache__", ".DS_Store"}


class ReleaseBuildError(Exception):
    pass


def release_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for relative in RELEASE_PATHS:
        source = repo_root / relative
        if source.is_file():
            files.append(source)
            continue
        if source.is_dir():
            files.extend(
                path
                for path in source.rglob("*")
                if path.is_file() and not (set(path.parts) & IGNORED_PARTS)
            )
            continue
        raise ReleaseBuildError(f"required release path is missing: {relative}")

    for path in files:
        if path.is_symlink():
            raise ReleaseBuildError(f"release input must not be a symlink: {path}")
        try:
            path.resolve().relative_to(repo_root.resolve())
        except ValueError as exc:
            raise ReleaseBuildError(f"release input escapes repository: {path}") from exc
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ReleaseBuildError(
                f"non-UTF-8 release input requires an explicit policy: {path}"
            ) from exc
    return sorted(files, key=lambda path: path.relative_to(repo_root).as_posix())


def build_release(repo_root: Path = REPO_ROOT, output_dir: Path | None = None) -> Path:
    repo_root = repo_root.resolve()
    version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER_RE.fullmatch(version):
        raise ReleaseBuildError(f"invalid VERSION: {version!r}")

    output_dir = (output_dir or (repo_root / "dist")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"mileswang-skill-v{version}.zip"
    prefix = f"mileswang-skill-v{version}"

    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in release_files(repo_root):
            relative = path.relative_to(repo_root).as_posix()
            info = zipfile.ZipInfo(f"{prefix}/{relative}", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes(), compresslevel=9)

    return archive_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the deterministic mileswang-skill release zip."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "dist",
        help="destination directory (default: ./dist)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        archive = build_release(output_dir=args.output_dir)
    except (OSError, ReleaseBuildError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
