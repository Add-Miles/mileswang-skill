#!/usr/bin/env python3
"""Read X Memory local data for Codex / scripts (read-only, no network)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def data_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "XMemory"
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home())) / "XMemory"
    return Path.home() / ".local" / "share" / "XMemory"


def day_today() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d")


def day_offset(n: int) -> str:
    d = datetime.now().astimezone().date() + timedelta(days=n)
    return d.strftime("%Y-%m-%d")


def load_views(day: str) -> list[dict[str, Any]]:
    path = data_dir() / "views" / f"{day}.jsonl"
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def load_post(post_id: str) -> dict[str, Any] | None:
    path = data_dir() / "posts" / f"{post_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def body_of(post: dict[str, Any]) -> str:
    text = (post.get("text") or "").strip()
    if text:
        return text
    article = post.get("article") or {}
    if isinstance(article, dict):
        md = (article.get("body_markdown") or "").strip()
        if md:
            title = (article.get("title") or "").strip()
            return f"# {title}\n\n{md}" if title else md
        if article.get("title"):
            return str(article["title"])
    jina = (post.get("jina_markdown") or "").strip()
    return jina


def summarize_day(day: str) -> dict[str, Any]:
    views = load_views(day)
    posts: dict[str, Any] = {}
    for v in views:
        pid = v.get("postId")
        if not pid or pid in posts:
            continue
        posts[pid] = load_post(str(pid))

    opened = len(views)
    summarizable = 0
    failed = 0
    hydrated = 0
    items = []
    for v in views:
        pid = str(v.get("postId") or "")
        post = posts.get(pid) if pid in posts else load_post(pid)
        status = (post or {}).get("status") if post else "missing"
        body = body_of(post) if post else ""
        if status == "summarizable" or body:
            if body:
                summarizable += 1
            else:
                hydrated += 1
        elif status == "failed":
            failed += 1
        author = (post or {}).get("author") or {}
        items.append({
            "view": v,
            "status": status,
            "canonicalUrl": (post or {}).get("canonicalUrl") or v.get("canonicalUrl"),
            "author": author,
            "text": body,
            "quote": (post or {}).get("quote"),
            "article": (post or {}).get("article"),
            "backend": (post or {}).get("backend"),
            "errors": (post or {}).get("errors") or [],
        })

    return {
        "day": day,
        "dataDir": str(data_dir()),
        "opened": opened,
        "summarizable": summarizable,
        "failed": failed,
        "read": sum(1 for v in views if v.get("readingClass") == "read"),
        "glance": sum(1 for v in views if v.get("readingClass") == "glance"),
        "revisit": sum(1 for v in views if v.get("readingClass") == "revisit"),
        "items": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only X Memory dump")
    parser.add_argument("--day", default=None, help="YYYY-MM-DD (default today)")
    parser.add_argument("--yesterday", action="store_true")
    parser.add_argument("--failures", action="store_true")
    args = parser.parse_args()

    if args.failures:
        path = data_dir() / "state" / "failures.jsonl"
        rows = []
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        print(json.dumps({"failures": rows}, ensure_ascii=False, indent=2))
        return 0

    day = args.day or (day_offset(-1) if args.yesterday else day_today())
    print(json.dumps(summarize_day(day), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
