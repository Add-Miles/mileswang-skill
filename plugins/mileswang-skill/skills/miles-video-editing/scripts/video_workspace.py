#!/usr/bin/env python3
"""Portable, fail-closed workspace tooling for Miles V10 video editing."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PIN = "0.7.81"
MIN_NODE = 22
MIN_PYTHON = (3, 10)


class ContractError(RuntimeError):
    pass


def emit(payload: dict[str, Any], as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def version(command: str) -> str | None:
    path = shutil.which(command)
    if not path:
        return None
    result = run([path, "--version"])
    text = (result.stdout or result.stderr).strip().splitlines()
    return text[0] if text else "unknown"


def major(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"(?:^|\s)v?(\d+)(?:\.|\s)", value)
    return int(match.group(1)) if match else None


def probe(path: Path) -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise ContractError("ffprobe is unavailable")
    result = run([
        ffprobe, "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ])
    if result.returncode:
        raise ContractError(f"ffprobe failed: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not video:
        raise ContractError("input has no video stream")
    if not audio:
        raise ContractError("input has no audio stream")
    duration = float(data.get("format", {}).get("duration") or video.get("duration") or 0)
    if duration <= 0:
        raise ContractError("input duration is unavailable")
    return {
        "duration": duration,
        "width": int(video["width"]),
        "height": int(video["height"]),
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name"),
    }


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def inside(root: Path, relative: str, *, must_exist: bool = False) -> Path:
    if Path(relative).is_absolute() or relative.startswith("~"):
        raise ContractError(f"path must be project-relative: {relative}")
    root = root.resolve()
    target = (root / relative).resolve(strict=must_exist)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ContractError(f"path escapes project: {relative}") from exc
    return target


def load_manifest(project: Path) -> dict[str, Any]:
    manifest_path = inside(project, "manifest.json", must_exist=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ("source", "transcript", "storyboard", "composition", "outputs"):
        value = manifest.get("paths", {}).get(key)
        if not isinstance(value, str):
            raise ContractError(f"manifest missing relative path: {key}")
        inside(project, value)
    return manifest


def preflight(args: argparse.Namespace) -> int:
    blockers: list[str] = []
    setup: list[str] = []
    versions = {name: version(name) for name in ("ffmpeg", "ffprobe", "node", "npm", "npx")}
    if sys.version_info < MIN_PYTHON:
        blockers.append("python>=3.10")
    for name in ("ffmpeg", "ffprobe", "node", "npm", "npx"):
        if versions[name] is None:
            blockers.append(name)
    if versions["node"] and (major(versions["node"]) or 0) < MIN_NODE:
        blockers.append("node>=22")
    media = None
    if args.input:
        try:
            source = Path(args.input).expanduser().resolve(strict=True)
            media = probe(source)
        except (OSError, ContractError, ValueError) as exc:
            blockers.append(str(exc))
    else:
        blockers.append("input video")
    setup.extend([
        f"project-local hyperframes@{PIN}",
        "HyperFrames managed browser",
        "local Whisper model on first transcription",
    ])
    payload = {
        "status": "blocked" if blockers else "setup_required",
        "render_started": False,
        "hyperframes_pin": PIN,
        "versions": versions,
        "media": media,
        "blockers": blockers,
        "setup_required": setup,
    }
    emit(payload, args.json)
    return 2 if blockers else 0


def init_project(args: argparse.Namespace) -> int:
    source = Path(args.input).expanduser().resolve(strict=True)
    media = probe(source)
    project = Path(args.project_dir).expanduser().resolve()
    if project.exists() and any(project.iterdir()):
        raise ContractError("project directory must be new or empty")
    if project == source.parent or project in source.parents:
        raise ContractError("project directory cannot contain or replace the source")
    for relative in (
        "source", "work/subtitles", "work/spec", "work/composition/assets",
        "work/snapshots", "outputs",
    ):
        (project / relative).mkdir(parents=True, exist_ok=True)
    copied = project / "source" / f"original{source.suffix.lower()}"
    shutil.copy2(source, copied)
    copied.chmod(0o444)
    sha = digest(copied)
    if sha != digest(source):
        raise ContractError("source copy hash mismatch")
    manifest = {
        "schema_version": 1,
        "status": "initialized",
        "source": {**media, "sha256": sha},
        "paths": {
            "source": copied.relative_to(project).as_posix(),
            "transcript": "work/transcript.srt",
            "storyboard": "work/spec/storyboard.json",
            "composition": "work/composition",
            "outputs": "outputs",
        },
        "executors": {"transcription": None, "composition": None, "render": None},
    }
    (project / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    emit({"status": "initialized", "project": str(project), "source_sha256": sha})
    return 0


def setup_project(args: argparse.Namespace) -> int:
    project = Path(args.project_dir).expanduser().resolve(strict=True)
    manifest = load_manifest(project)
    toolchain = inside(project, "work/toolchain")
    toolchain.mkdir(parents=True, exist_ok=True)
    package = {
        "private": True,
        "description": "Project-local public toolchain for Miles V10 editing",
        "devDependencies": {"hyperframes": PIN},
    }
    (toolchain / "package.json").write_text(
        json.dumps(package, indent=2) + "\n", encoding="utf-8"
    )
    npm = shutil.which("npm")
    if not npm:
        raise ContractError("npm is unavailable")
    install = run([
        npm, "install", "--prefix", str(toolchain), "--ignore-scripts",
        "--no-audit", "--no-fund",
    ])
    if install.returncode:
        raise ContractError(f"public npm setup failed: {install.stderr.strip()}")
    binary = toolchain / "node_modules" / ".bin" / "hyperframes"
    if not binary.is_file():
        raise ContractError("pinned HyperFrames executable was not installed")
    browser = run([str(binary), "browser", "ensure"])
    if browser.returncode:
        raise ContractError(f"HyperFrames browser setup failed: {browser.stderr.strip()}")
    manifest["status"] = "toolchain-ready"
    manifest["hyperframes_pin"] = PIN
    manifest["executors"] = {
        "transcription": "project-local-hyperframes-whisper",
        "composition": "miles-video-editing",
        "render": "project-local-hyperframes",
    }
    (project / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    emit({
        "status": "toolchain-ready",
        "hyperframes_pin": PIN,
        "api_key_required": False,
        "toolchain": "work/toolchain",
    }, args.json)
    return 0


def write_raw_whisper_srt(
    project: Path,
    source: Path,
    destination: Path,
    language: str,
    model: str,
) -> bool:
    whisper = shutil.which("whisper-cli")
    ffmpeg = shutil.which("ffmpeg")
    model_path = Path.home() / ".cache" / "hyperframes" / "whisper" / "models" / f"ggml-{model}.bin"
    if not whisper or not ffmpeg or not model_path.is_file():
        return False
    work = inside(project, "work/transcription")
    work.mkdir(parents=True, exist_ok=True)
    audio = work / "audio.wav"
    extract = run([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(source),
        "-vn", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
        "-y", str(audio),
    ])
    if extract.returncode:
        raise ContractError(f"local transcription audio extraction failed: {extract.stderr.strip()}")
    prefix = work / "whisper"
    result = run([
        whisper, "-m", str(model_path), "-l", language, "-oj", "-of",
        str(prefix), "-np", str(audio),
    ])
    if result.returncode:
        raise ContractError(f"whisper-cli failed: {result.stderr.strip()}")
    raw_path = prefix.with_suffix(".json")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    segments = raw.get("transcription", [])
    if not segments:
        raise ContractError("whisper-cli returned no speech segments")
    blocks: list[str] = []
    for index, segment in enumerate(segments, start=1):
        text = str(segment.get("text", "")).strip()
        timestamps = segment.get("timestamps", {})
        start, end = timestamps.get("from"), timestamps.get("to")
        if not text or "\ufffd" in text or not start or not end:
            raise ContractError("local transcript contains invalid text or timestamps")
        blocks.append(f"{index}\n{start} --> {end}\n{text}")
    destination.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    return True


def transcribe_project(args: argparse.Namespace) -> int:
    project = Path(args.project_dir).expanduser().resolve(strict=True)
    manifest = load_manifest(project)
    binary = inside(
        project, "work/toolchain/node_modules/.bin/hyperframes", must_exist=True
    )
    source = inside(project, manifest["paths"]["source"], must_exist=True)
    result = run([
        str(binary), "transcribe", str(source), "--engine", "whisper",
        "--model", args.model, "--language", args.language,
        "--dir", str(project), "--json",
    ])
    if result.returncode:
        raise ContractError(f"local transcription failed: {result.stderr.strip()}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ContractError("local transcription returned invalid JSON") from exc
    if not payload.get("ok") or not payload.get("transcriptPath"):
        raise ContractError(f"local transcription failed: {payload.get('error', 'unknown error')}")
    transcript_json = Path(payload["transcriptPath"]).resolve(strict=True)
    try:
        transcript_json.relative_to(project)
    except ValueError as exc:
        raise ContractError("transcription output escaped the project") from exc
    srt = inside(project, manifest["paths"]["transcript"])
    used_raw_cli = write_raw_whisper_srt(
        project, source, srt, args.language, args.model
    )
    if not used_raw_cli:
        export = run([
            str(binary), "transcribe", str(transcript_json), "--to", "srt",
            "--output", str(srt), "--preserve-cues", "--dir", str(project),
        ])
        if export.returncode:
            raise ContractError(f"SRT export failed: {export.stderr.strip()}")
    if not srt.is_file() or not srt.read_text(encoding="utf-8").strip():
        raise ContractError("SRT export produced no transcript")
    if "\ufffd" in srt.read_text(encoding="utf-8"):
        raise ContractError(
            "local transcript contains replacement characters; provide a reviewed SRT or authorize another executor"
        )
    emit({
        "status": "transcribed-local",
        "engine": "whisper-cli" if used_raw_cli else "hyperframes-whisper",
        "model": args.model,
        "language": args.language,
        "api_key_required": False,
        "transcript": manifest["paths"]["transcript"],
    }, args.json)
    return 0


def load_storyboard(project: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    path = inside(project, manifest["paths"]["storyboard"], must_exist=True)
    return json.loads(path.read_text(encoding="utf-8"))


def intervals(items: list[dict[str, Any]], duration: float, label: str) -> None:
    ids: set[str] = set()
    lanes: dict[str, list[tuple[float, float, str]]] = {}
    for item in items:
        uid = item.get("id")
        if not isinstance(uid, str) or not uid or uid in ids:
            raise ContractError(f"{label} has missing or duplicate id")
        ids.add(uid)
        start, end = float(item.get("start", -1)), float(item.get("end", -1))
        if start < 0 or end <= start or end > duration + 0.04:
            raise ContractError(f"{label} {uid} is outside source duration")
        lane = str(item.get("lane", label))
        for old_start, old_end, old_id in lanes.setdefault(lane, []):
            if start < old_end and end > old_start:
                raise ContractError(f"{label} {uid} overlaps {old_id} on lane {lane}")
        lanes[lane].append((start, end, uid))


def validate_project(project: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_manifest(project)
    source = inside(project, manifest["paths"]["source"], must_exist=True)
    if source.is_symlink() or digest(source) != manifest["source"]["sha256"]:
        raise ContractError("source identity mismatch")
    transcript = inside(project, manifest["paths"]["transcript"], must_exist=True)
    if not transcript.read_text(encoding="utf-8").strip():
        raise ContractError("timestamped transcript is empty")
    board = load_storyboard(project, manifest)
    duration = float(manifest["source"]["duration"])
    if board.get("schema_version") != 1:
        raise ContractError("unsupported storyboard schema_version")
    source_meta = board.get("source", {})
    if source_meta.get("sha256") != manifest["source"]["sha256"]:
        raise ContractError("storyboard source hash mismatch")
    if abs(float(source_meta.get("duration", 0)) - duration) > 0.04:
        raise ContractError("storyboard duration mismatch")
    output = board.get("output", {})
    if (output.get("width"), output.get("height")) != (1080, 1920):
        raise ContractError("V10 output must be 1080x1920")
    beats = board.get("beats")
    if not isinstance(beats, list) or not beats:
        raise ContractError("storyboard needs semantic beats")
    intervals(beats, duration, "beats")
    ordered = sorted(beats, key=lambda item: item["start"])
    cursor = 0.0
    for beat in ordered:
        if abs(float(beat["start"]) - cursor) > 0.08:
            raise ContractError("semantic beats must cover the full source without gaps")
        cursor = float(beat["end"])
        for field in ("claim", "title", "detail", "reason", "treatment", "slot"):
            if not str(beat.get(field, "")).strip():
                raise ContractError(f"beat {beat['id']} missing {field}")
        if not beat.get("tags"):
            raise ContractError(f"beat {beat['id']} needs tags")
        top = int(beat.get("top", 105))
        if top < 0 or top > 900:
            raise ContractError(f"beat {beat['id']} top position is outside the safe range")
    if abs(cursor - duration) > 0.08:
        raise ContractError("semantic beats do not reach source end")
    captions = board.get("captions", [])
    events = board.get("events", [])
    intervals(captions, duration, "captions")
    intervals(events, duration, "events")
    if any(item.get("slot") == "lower" for item in events):
        raise ContractError("auxiliary events may not occupy the lower caption zone")
    missing = [a.get("id") for a in board.get("assets", []) if a.get("required") and a.get("status") == "missing"]
    if missing:
        raise ContractError(f"required assets are missing: {', '.join(map(str, missing))}")
    return manifest, board


def validate_command(args: argparse.Namespace) -> int:
    _, board = validate_project(Path(args.project_dir).expanduser().resolve(strict=True))
    emit({"status": "valid", "beats": len(board["beats"]), "captions": len(board.get("captions", [])), "events": len(board.get("events", []))}, args.json)
    return 0


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def clip(uid: str, start: float, end: float, track: int, class_name: str, body: str) -> str:
    return f'<section id="{esc(uid)}" class="clip {class_name}" data-start="{start:.4f}" data-duration="{end-start:.4f}" data-track-index="{track}">{body}</section>'


def build_command(args: argparse.Namespace) -> int:
    project = Path(args.project_dir).expanduser().resolve(strict=True)
    manifest, board = validate_project(project)
    composition = inside(project, manifest["paths"]["composition"])
    assets = composition / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    source = inside(project, manifest["paths"]["source"], must_exist=True)
    target = assets / f"input{source.suffix.lower()}"
    if target.exists():
        target.chmod(0o644)
        target.unlink()
    shutil.copy2(source, target)
    duration = float(manifest["source"]["duration"])
    fps = int(board["output"].get("fps", 30))
    pieces = [f'<video id="a-roll" src="assets/{target.name}" data-start="0" data-duration="{duration:.4f}" data-track-index="0" muted playsinline></video>', f'<audio id="a-roll-audio" src="assets/{target.name}" data-start="0" data-duration="{duration:.4f}" data-track-index="20" data-volume="1"></audio>']
    for index, beat in enumerate(board["beats"]):
        tags = "".join(f"<span>{esc(tag)}</span>" for tag in beat["tags"][:4])
        body = f'<div class="card-inner"><small>{esc(beat.get("kicker", "SEMANTIC BEAT"))}</small><h2>{esc(beat["title"])}</h2><p>{esc(beat["detail"])}</p><div class="tags">{tags}</div></div>'
        beat_clip = clip(beat["id"], float(beat["start"]), float(beat["end"]), 2 + index, f"beat slot-{esc(beat['slot'])}", body)
        beat_clip = beat_clip.replace(
            f"beat slot-{esc(beat['slot'])}",
            f"beat slot-{esc(beat['slot'])} treatment-{esc(beat['treatment'])}",
        )
        pieces.append(beat_clip.replace(">", f' style="top:{int(beat.get("top", 105))}px">', 1))
    for index, event in enumerate(board.get("events", [])):
        body = f'<div class="micro-inner"><small>{esc(event.get("label", "SIGNAL"))}</small><strong>{esc(event.get("text", ""))}</strong></div>'
        pieces.append(clip(event["id"], float(event["start"]), float(event["end"]), 40 + index, f"micro slot-{esc(event.get('slot', 'right'))}", body))
    for index, caption in enumerate(board.get("captions", [])):
        pieces.append(clip(caption["id"], float(caption["start"]), float(caption["end"]), 100 + index, "caption", f'<div>{esc(caption.get("text", ""))}</div>'))
    html_text = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080,height=1920"><title>Miles V10 Portable</title>
<style>
html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#111;color:#fff;font-family:Roboto,sans-serif}}*{{box-sizing:border-box}}#root{{position:relative;width:1080px;height:1920px;overflow:hidden}}#root::before{{content:"";position:absolute;inset:0;background:#111;z-index:-2}}video{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:0}}.clip{{position:absolute;z-index:3}}.beat{{width:660px;top:105px}}.slot-left{{left:38px}}.slot-right{{right:38px}}.slot-hero{{left:50%;transform:translateX(-50%)}}.card-inner{{padding:30px;border:1px solid rgba(210,255,235,.32);border-radius:24px;background:linear-gradient(145deg,rgba(8,22,18,.97),rgba(13,24,22,.94));box-shadow:0 22px 70px rgba(0,0,0,.42)}}.treatment-full-screen-answer{{inset:0!important;width:1080px;height:1920px;transform:none!important;z-index:8;background:#07120f}}.treatment-full-screen-answer .card-inner{{width:100%;height:100%;border:0;border-radius:0;display:flex;flex-direction:column;justify-content:center;padding:120px;background:radial-gradient(circle at 50% 38%,#17352b 0%,#07120f 64%)}}.treatment-full-screen-answer h2{{font-size:72px;max-width:840px}}.treatment-full-screen-answer p{{font-size:34px;max-width:800px}}small{{color:#c9ffe9;font-weight:800;letter-spacing:2px}}h2{{font-size:52px;line-height:1.08;margin:14px 0 12px}}p{{font-size:27px;line-height:1.42;margin:0;color:#f2f6f3}}.tags{{display:flex;gap:10px;margin-top:18px;flex-wrap:wrap}}.tags span{{padding:8px 14px;border:1px solid #f0cf55;border-radius:999px;color:#ffe993;font-size:20px}}.micro{{width:310px;top:720px}}.micro-inner{{padding:18px 22px;border-radius:18px;background:rgba(7,18,15,.96);box-shadow:0 14px 38px rgba(0,0,0,.38)}}.micro strong{{display:block;font-size:28px;margin-top:7px}}.caption{{left:64px;right:64px;bottom:68px;text-align:center;z-index:9}}.caption div{{display:inline-block;max-width:952px;padding:18px 26px;border-radius:18px;background:rgba(0,0,0,.72);font-size:38px;font-weight:750;line-height:1.28;text-shadow:0 2px 3px #000}}
</style></head><body><div id="root" data-composition-id="miles-v10" data-no-timeline data-start="0" data-width="1080" data-height="1920" data-duration="{duration:.4f}" data-fps="{fps}">{''.join(pieces)}</div>
<script>document.querySelectorAll('.beat .card-inner,.micro .micro-inner,.caption div').forEach((el)=>{{const host=el.closest('.clip');const start=Number(host.dataset.start)*1000;const total=Number(host.dataset.duration)*1000;const anim=el.animate([{{transform:'translateY(24px) scale(.98)'}},{{transform:'translateY(0) scale(1)',offset:.18}},{{transform:'translateY(0) scale(1)',offset:.88}},{{transform:'translateY(-10px) scale(.99)'}}],{{duration:total,delay:start,easing:'cubic-bezier(.2,0,0,1)',fill:'both',iterations:1}});anim.pause();}});</script></body></html>'''
    (composition / "index.html").write_text(html_text, encoding="utf-8")
    package = {"private": True, "scripts": {"check": "hyperframes check --strict", "preview": "hyperframes preview", "render": "hyperframes render --quality high"}, "devDependencies": {"hyperframes": PIN}}
    (composition / "package.json").write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    manifest["status"] = "composition-built"
    manifest["hyperframes_pin"] = PIN
    (project / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    emit({"status": "composition-built", "composition": str(composition), "hyperframes_pin": PIN})
    return 0


def verify_command(args: argparse.Namespace) -> int:
    project = Path(args.project_dir).expanduser().resolve(strict=True)
    output = inside(project, args.output, must_exist=True)
    if output.stat().st_size == 0:
        raise ContractError("render output is empty")
    media = probe(output)
    blockers = []
    if (media["width"], media["height"]) != (1080, 1920):
        blockers.append("output is not 1080x1920")
    if media["video_codec"] != "h264":
        blockers.append("output video codec is not h264")
    if media["audio_codec"] != "aac":
        blockers.append("output audio codec is not aac")
    payload = {"status": "candidate" if not blockers else "rejected", "output": args.output, "media": media, "blockers": blockers}
    emit(payload, args.json)
    return 0 if not blockers else 2


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)
    pre = commands.add_parser("preflight")
    pre.add_argument("--input")
    pre.add_argument("--json", action="store_true")
    init = commands.add_parser("init")
    init.add_argument("--input", required=True)
    init.add_argument("--project-dir", required=True)
    setup = commands.add_parser("setup")
    setup.add_argument("--project-dir", required=True)
    setup.add_argument("--json", action="store_true")
    transcribe = commands.add_parser("transcribe")
    transcribe.add_argument("--project-dir", required=True)
    transcribe.add_argument("--language", default="zh")
    transcribe.add_argument("--model", default="small")
    transcribe.add_argument("--json", action="store_true")
    val = commands.add_parser("validate")
    val.add_argument("--project-dir", required=True)
    val.add_argument("--json", action="store_true")
    build = commands.add_parser("build")
    build.add_argument("--project-dir", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--project-dir", required=True)
    verify.add_argument("--output", required=True)
    verify.add_argument("--json", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    handlers = {
        "preflight": preflight,
        "init": init_project,
        "setup": setup_project,
        "transcribe": transcribe_project,
        "validate": validate_command,
        "build": build_command,
        "verify": verify_command,
    }
    try:
        return handlers[args.command](args)
    except (ContractError, OSError, ValueError, json.JSONDecodeError) as exc:
        emit({"status": "blocked", "render_started": False, "error": str(exc)}, getattr(args, "json", False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
