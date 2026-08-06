#!/usr/bin/env python3
"""Build / maintain a durable ledger of Skill shares found in X Memory posts.

Output (macOS):
  ~/Library/Application Support/XMemory/skills/
    skills.jsonl   # one line per unique (skill_id, post_id)
    index.md       # human-readable catalog (regenerated)

CLI:
  python3 skill_ledger.py                 # rescan all posts + rewrite index
  python3 skill_ledger.py --list          # print index.md
  python3 skill_ledger.py --post-id ID    # extract one post only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def data_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "XMemory"
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home())) / "XMemory"
    return Path.home() / ".local" / "share" / "XMemory"


SKILLS_DIR = data_dir() / "skills"
LEDGER_PATH = SKILLS_DIR / "skills.jsonl"
INDEX_PATH = SKILLS_DIR / "index.md"
POSTS_DIR = data_dir() / "posts"

GITHUB_RE = re.compile(
    r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/tree/[^ \n)]+)?",
    re.I,
)
# skill name candidates
NAME_PATTERNS = [
    re.compile(r"(?:skill|Skill)\s*[:：]\s*([a-zA-Z0-9][a-zA-Z0-9_./-]{2,80})", re.I),
    re.compile(r"(?:开源|分享|发布|推荐).{0,12}?(?:skill|Skill)\s*[:：]?\s*([a-zA-Z0-9][a-zA-Z0-9_./-]{2,80})", re.I),
    re.compile(r"\b([a-z0-9][a-z0-9_-]{2,40}-(?:skill|slicer|agent|cli|tools?))\b", re.I),
    re.compile(r"\$([a-zA-Z0-9][a-zA-Z0-9_-]{2,40})", re.I),  # $skill-name style
    re.compile(r"`([a-zA-Z0-9][a-zA-Z0-9_./-]{2,60})`", re.I),
]

# must mention skill-ish vocabulary to reduce false positives on bare github links
SIGNAL_RE = re.compile(
    r"\bskill\b|Skill|技能|开源一个|Claude Code|Codex|cursor\s*skill|agents?/skills",
    re.I,
)

# first-sentence problem statements after name
PROBLEM_PATTERNS = [
    re.compile(r"(?:Skill|skill)[：:，,\s]+(.{8,120}?)(?:\n|。|！|？)"),
    re.compile(r"(?:解决|用于|可以|帮你|让你|一键)(.{6,100}?)(?:\n|。|！)"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def body_of(post: dict[str, Any]) -> str:
    text = (post.get("text") or "").strip()
    if text:
        return text
    article = post.get("article") or {}
    if isinstance(article, dict):
        md = (article.get("body_markdown") or article.get("title") or "").strip()
        if md:
            return md
    return (post.get("jina_markdown") or "").strip()


def looks_like_skill_share(text: str) -> bool:
    if not text or not SIGNAL_RE.search(text):
        return False
    # need name, github, or package-like token
    if GITHUB_RE.search(text):
        return True
    if any(p.search(text) for p in NAME_PATTERNS[:3]):
        return True
    if re.search(r"安装|下载到|放入\s*~/.|Codex|Claude", text, re.I):
        return True
    return False


def extract_names(text: str, githubs: list[str]) -> list[str]:
    names: list[str] = []
    for pat in NAME_PATTERNS:
        for m in pat.finditer(text):
            n = m.group(1).strip().strip(".,;:，。；：/ ")
            if n.lower() in {"skill", "skills", "codex", "claude", "github", "http", "https"}:
                continue
            if len(n) < 3:
                continue
            names.append(n)
    for g in githubs:
        # .../tree/main/yichen-x-slicer or .../repo
        parts = g.rstrip("/").split("/")
        if "tree" in parts:
            i = parts.index("tree")
            if i + 2 < len(parts):
                names.append(parts[i + 2])
        if parts:
            names.append(parts[-1])
    # preserve order unique
    out: list[str] = []
    seen: set[str] = set()
    for n in names:
        key = n.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(n)
    return out


def extract_problem(text: str, skill_name: str) -> str:
    # Prefer sentence containing skill name
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if skill_name.lower() in line.lower() or "skill" in line.lower():
            # strip name lead-in
            cleaned = re.sub(
                r"^.*?(?:skill|Skill)[：:]\s*" + re.escape(skill_name) + r"[，,\s]*",
                "",
                line,
                flags=re.I,
            )
            cleaned = cleaned or line
            if len(cleaned) >= 8:
                return cleaned[:160]
    for pat in PROBLEM_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1).strip()[:160]
    # first non-empty line
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line[:160]
    return ""


def extract_how_to(text: str) -> str:
    markers = ("使用方法", "怎么用", "用法", "安装", "步骤", "下载到", "发给")
    lines = text.splitlines()
    chunks: list[str] = []
    for i, line in enumerate(lines):
        if any(m in line for m in markers):
            chunk = " ".join(l.strip() for l in lines[i : i + 3] if l.strip())
            chunks.append(chunk[:220])
            break
    if chunks:
        return chunks[0]
    # fallback short
    if "Codex" in text or "Claude" in text:
        m = re.search(r".{0,40}(?:Codex|Claude|安装|下载).{0,80}", text)
        if m:
            return m.group(0).replace("\n", " ")[:220]
    return ""


def extract_from_post(post: dict[str, Any]) -> list[dict[str, Any]]:
    text = body_of(post)
    if not looks_like_skill_share(text):
        return []
    githubs = GITHUB_RE.findall(text)
    names = extract_names(text, githubs)
    if not names and not githubs:
        return []
    if not names and githubs:
        names = [githubs[0].rstrip("/").split("/")[-1]]

    # pull phrases like "yichen-unified-search Skill"
    for m in re.finditer(
        r"([a-zA-Z0-9][a-zA-Z0-9_.-]{2,60})\s+Skill\b", text, re.I
    ):
        n = m.group(1)
        if n.lower() not in {x.lower() for x in names}:
            names.append(n)

    author = post.get("author") or {}
    handle = author.get("screen_name") if isinstance(author, dict) else None
    author_name = author.get("name") if isinstance(author, dict) else None

    if not names:
        return []

    primary = names[0]
    related: list[str] = []
    for n in names[1:]:
        if n.lower() == primary.lower():
            continue
        if re.search(
            r"(前提|先装|依赖|安装我的).{0,40}" + re.escape(n), text, re.I
        ) or re.search(re.escape(n) + r".{0,12}Skill", text, re.I):
            related.append(n)
        elif re.search(r"skill|slicer|agent", n, re.I):
            related.append(n)
    related = related[:6]

    how = extract_how_to(text)
    problem = extract_problem(text, primary)
    skill_id = re.sub(r"[^a-zA-Z0-9._/-]+", "-", primary).strip("-").lower()

    entry = {
        "schema_version": "1.0",
        "kind": "skill_share",
        "skill_id": skill_id,
        "skill_name": primary,
        "problem": problem,
        "how_to_use": how,
        "repo_urls": githubs,
        "related_skills": related,
        "author_handle": handle,
        "author_name": author_name,
        "source_post_id": post.get("postId"),
        "source_url": post.get("canonicalUrl"),
        "backend": post.get("backend"),
        "extracted_at": utc_now(),
        "status": "active",
    }
    return [entry]


def load_ledger() -> list[dict[str, Any]]:
    if not LEDGER_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def ledger_key(row: dict[str, Any]) -> str:
    return f"{row.get('skill_id')}|{row.get('source_post_id')}"


def save_ledger(rows: list[dict[str, Any]]) -> None:
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    # stable order: newest extracted first in index; file chronological by skill_id
    rows_sorted = sorted(
        rows,
        key=lambda r: (str(r.get("skill_id") or ""), str(r.get("extracted_at") or "")),
    )
    with LEDGER_PATH.open("w", encoding="utf-8") as f:
        for r in rows_sorted:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def upsert_entries(entries: list[dict[str, Any]]) -> int:
    if not entries:
        return 0
    existing = {ledger_key(r): r for r in load_ledger()}
    added = 0
    for e in entries:
        k = ledger_key(e)
        if k in existing:
            # merge non-empty upgrades
            old = existing[k]
            for field in ("problem", "how_to_use", "repo_urls", "related_skills"):
                if e.get(field) and (not old.get(field) or len(str(e.get(field))) > len(str(old.get(field) or ""))):
                    old[field] = e[field]
            old["updated_at"] = utc_now()
            existing[k] = old
        else:
            existing[k] = e
            added += 1
    save_ledger(list(existing.values()))
    return added


def write_index(rows: list[dict[str, Any]] | None = None) -> None:
    rows = rows if rows is not None else load_ledger()
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    # newest first in catalog
    rows = sorted(rows, key=lambda r: str(r.get("extracted_at") or ""), reverse=True)
    lines = [
        "# X Memory · Skill 分享沉淀",
        "",
        f"更新时间：{utc_now()}",
        f"条目数：{len(rows)}",
        "",
        "字段：博主 · Skill · 解决什么问题 · 怎么用 · 仓库 · 原帖",
        "",
    ]
    if not rows:
        lines.append("_暂无 Skill 分享记录。打开带 Skill 的 X 帖后会自动追加。_")
    for i, r in enumerate(rows, 1):
        author = r.get("author_handle") or r.get("author_name") or "?"
        if r.get("author_handle"):
            author = f"@{r['author_handle']}"
        repos = r.get("repo_urls") or []
        repo_s = ", ".join(repos) if repos else "—"
        related = r.get("related_skills") or []
        rel_s = ", ".join(related) if related else "—"
        lines.extend(
            [
                f"## {i}. {r.get('skill_name') or r.get('skill_id')}",
                f"- **博主**：{author}",
                f"- **解决什么问题**：{r.get('problem') or '—'}",
                f"- **怎么用**：{r.get('how_to_use') or '—'}",
                f"- **仓库 / 入口**：{repo_s}",
                f"- **相关 Skill**：{rel_s}",
                f"- **原帖**：{r.get('source_url') or '—'}",
                f"- **记录时间**：{r.get('extracted_at') or '—'}",
                "",
            ]
        )
    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def scan_all_posts() -> dict[str, int]:
    if not POSTS_DIR.exists():
        return {"posts": 0, "skill_posts": 0, "added": 0}
    posts = 0
    skill_posts = 0
    all_entries: list[dict[str, Any]] = []
    for path in POSTS_DIR.glob("*.json"):
        try:
            post = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        posts += 1
        if not isinstance(post, dict):
            continue
        entries = extract_from_post(post)
        if entries:
            skill_posts += 1
            all_entries.extend(entries)
    added = upsert_entries(all_entries)
    write_index()
    return {"posts": posts, "skill_posts": skill_posts, "added": added, "total": len(load_ledger())}


def scan_one(post_id: str) -> dict[str, Any]:
    path = POSTS_DIR / f"{post_id}.json"
    if not path.exists():
        return {"ok": False, "error": "missing_post"}
    post = json.loads(path.read_text(encoding="utf-8"))
    entries = extract_from_post(post)
    added = upsert_entries(entries)
    write_index()
    return {"ok": True, "entries": entries, "added": added, "total": len(load_ledger())}


def process_post_dict(post: dict[str, Any]) -> list[dict[str, Any]]:
    """API used by native host after hydrate."""
    entries = extract_from_post(post)
    if entries:
        upsert_entries(entries)
        write_index()
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="X Memory skill share ledger")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--post-id")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.list:
        write_index()
        if INDEX_PATH.exists():
            print(INDEX_PATH.read_text(encoding="utf-8"))
        else:
            print("empty")
        return 0

    if args.post_id:
        result = scan_one(args.post_id)
    else:
        result = scan_all_posts()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if INDEX_PATH.exists():
            print(f"\nindex: {INDEX_PATH}")
            print(f"ledger: {LEDGER_PATH}")
    return 0 if result.get("ok", True) is not False else 1


if __name__ == "__main__":
    raise SystemExit(main())
