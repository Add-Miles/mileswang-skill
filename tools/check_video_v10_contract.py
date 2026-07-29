#!/usr/bin/env python3
"""Check that the public V10 skill remains portable and fail-closed."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "plugins/mileswang-skill/skills/miles-video-editing"


def main() -> int:
    required = [
        ROOT / "SKILL.md",
        ROOT / "scripts/video_workspace.py",
        ROOT / "references/v10-contract.md",
        ROOT / "references/dependencies.md",
        ROOT / "references/storyboard.schema.json",
    ]
    missing = [str(path.relative_to(REPO)) for path in required if not path.is_file()]
    if missing:
        print("FAIL: missing " + ", ".join(missing), file=sys.stderr)
        return 1
    json.loads(required[-1].read_text(encoding="utf-8"))
    text = "\n".join(path.read_text(encoding="utf-8") for path in required[:-1])
    private_patterns = [
        "/" + r"Users/[^<\s]+/",
        "/" + r"home/[^<\s]+/",
        "C:" + r"\\Users\\",
        "file" + "://",
    ]
    for pattern in private_patterns:
        if re.search(pattern, text):
            print(f"FAIL: private path pattern {pattern}", file=sys.stderr)
            return 1
    for marker in (
        "preflight", "setup", "transcribe", "render_started", "storyboard",
        "preview", "candidate", "api_key_required", "0.7.81",
    ):
        if marker not in text:
            print(f"FAIL: missing contract marker {marker}", file=sys.stderr)
            return 1
    print("PASS: portable V10 contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
