#!/usr/bin/env python3
"""Create a new internal skill without overwriting existing work."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS_ROOT = REPO_ROOT / "plugins" / "mileswang-skill" / "skills"


def validate_slug(slug: str) -> None:
    if len(slug) > 64 or not SLUG_RE.fullmatch(slug):
        raise ValueError(
            "skill name must be 1-64 lowercase letters, digits, or single hyphens"
        )


def create_skill(slug: str, root: Path, description: str) -> Path:
    validate_slug(slug)
    description = " ".join(description.split())
    if not description:
        raise ValueError("description must not be empty")

    skill_dir = root / slug
    if skill_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing path: {skill_dir}")

    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "\n".join(
            [
                "---",
                f"name: {slug}",
                f"description: {description}",
                "---",
                "",
                f"# {slug}",
                "",
                "Replace this line with concise, imperative workflow instructions.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return skill_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold one new skill inside the mileswang-skill plugin."
    )
    parser.add_argument("slug", help="kebab-case skill name")
    parser.add_argument(
        "--description",
        default="TODO describe the capability and its explicit trigger conditions.",
        help="single-line frontmatter description",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_SKILLS_ROOT,
        help="skills directory; defaults to the plugin skills directory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        created = create_skill(args.slug, args.root.expanduser().resolve(), args.description)
    except (ValueError, FileExistsError) as exc:
        raise SystemExit(str(exc)) from exc
    print(created)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
