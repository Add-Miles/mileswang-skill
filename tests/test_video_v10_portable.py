from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "plugins/mileswang-skill/skills/miles-video-editing/scripts/video_workspace.py"


def load_module():
    spec = importlib.util.spec_from_file_location("video_workspace", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class PortableV10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def make_source(self, root: Path, duration: float = 2.0) -> Path:
        if not shutil.which("ffmpeg"):
            self.skipTest("ffmpeg unavailable")
        source = root / "anonymous-input.mp4"
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                "-i", f"color=c=0x23352f:s=360x640:d={duration}:r=30",
                "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                "-shortest", "-y", str(source),
            ],
            check=True,
        )
        return source

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["python3", str(SCRIPT), *args], text=True, capture_output=True)

    def initialized(self, root: Path) -> tuple[Path, dict]:
        source = self.make_source(root)
        project = root / "portable-project"
        result = self.run_cli("init", "--input", str(source), "--project-dir", str(project))
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        manifest = json.loads((project / "manifest.json").read_text())
        return project, manifest

    def write_evidence(self, project: Path, manifest: dict, *, missing_asset: bool = False) -> None:
        (project / "work/transcript.srt").write_text(
            "1\n00:00:00,000 --> 00:00:01,000\n这是匿名测试句。\n\n"
            "2\n00:00:01,000 --> 00:00:02,000\n它只验证执行路径。\n",
            encoding="utf-8",
        )
        duration = manifest["source"]["duration"]
        board = {
            "schema_version": 1,
            "source": {"duration": duration, "sha256": manifest["source"]["sha256"]},
            "output": {"width": 1080, "height": 1920, "fps": 30},
            "beats": [
                {"id": "beat-1", "start": 0, "end": duration, "lane": "beats", "claim": "执行路径需要真实产物", "kicker": "PATH TEST", "title": "不是返回成功就算完成", "detail": "必须生成、检查并探测真实视频。", "tags": ["输入", "执行", "验收"], "treatment": "semantic-card", "slot": "left", "top": 180, "reason": "把三个步骤压缩成可检查关系"}
            ],
            "captions": [
                {"id": "cap-1", "start": 0, "end": duration / 2, "lane": "caption-1", "text": "这是匿名测试句。"},
                {"id": "cap-2", "start": duration / 2, "end": duration, "lane": "caption-2", "text": "它只验证执行路径。"}
            ],
            "events": [
                {"id": "event-1", "start": 0.4, "end": min(duration, 1.1), "lane": "micro-1", "slot": "right", "label": "验证", "text": "真实输出"}
            ],
            "assets": [
                {"id": "asset-1", "required": missing_asset, "status": "missing" if missing_asset else "reconstructed", "provenance": "anonymous fixture"}
            ]
        }
        (project / "work/spec/storyboard.json").write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_init_uses_relative_paths_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.make_source(root)
            original_hash = self.module.digest(source)
            project, manifest = self.initialized(root)
            self.assertTrue(all(not Path(value).is_absolute() for value in manifest["paths"].values()))
            copied = project / manifest["paths"]["source"]
            self.assertFalse(copied.is_symlink())
            self.assertEqual(self.module.digest(copied), original_hash)

    def test_preflight_requires_only_public_local_toolchain(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.make_source(Path(tmp))
            result = self.run_cli("preflight", "--input", str(source), "--json")
            self.assertEqual(result.returncode, 0, result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "setup_required")
            requirements = " ".join(payload["setup_required"])
            self.assertIn("project-local hyperframes@0.7.81", requirements)
            self.assertIn("local Whisper", requirements)
            self.assertNotIn("active hyperframes", requirements)
            self.assertNotIn("active timestamped", requirements)

    def test_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(self.module.ContractError):
                self.module.inside(Path(tmp), "../escape")

    def test_missing_required_asset_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, manifest = self.initialized(Path(tmp))
            self.write_evidence(project, manifest, missing_asset=True)
            result = self.run_cli("validate", "--project-dir", str(project), "--json")
            self.assertEqual(result.returncode, 2)
            self.assertIn("required assets are missing", result.stdout)
            self.assertIn('"render_started": false', result.stdout)

    def test_build_is_portable_and_pinned_without_private_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, manifest = self.initialized(Path(tmp))
            self.write_evidence(project, manifest)
            result = self.run_cli("build", "--project-dir", str(project))
            self.assertEqual(result.returncode, 0, result.stdout)
            composition = project / "work/composition"
            package = json.loads((composition / "package.json").read_text())
            self.assertEqual(package["devDependencies"]["hyperframes"], "0.7.81")
            page = (composition / "index.html").read_text()
            self.assertIn("data-composition-id=\"miles-v10\"", page)
            self.assertIn("data-no-timeline", page)
            self.assertIn("#c9ffe9", page)
            self.assertIn("style=\"top:180px\"", page)
            self.assertIn("treatment-semantic-card", page)
            self.assertIn("el.animate", page)
            self.assertNotIn("opacity:0", page)
            self.assertNotIn("gsap", page.lower())
            self.assertNotIn("/" + "Users/", page)
            self.assertTrue((composition / "assets/input.mp4").is_file())
            rebuilt = self.run_cli("build", "--project-dir", str(project))
            self.assertEqual(rebuilt.returncode, 0, rebuilt.stdout)

    def test_verify_rejects_wrong_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, _ = self.initialized(Path(tmp))
            wrong = self.make_source(project / "outputs")
            wrong.rename(project / "outputs/wrong.mp4")
            result = self.run_cli("verify", "--project-dir", str(project), "--output", "outputs/wrong.mp4", "--json")
            self.assertEqual(result.returncode, 2)
            self.assertIn('"status": "rejected"', result.stdout)


if __name__ == "__main__":
    unittest.main()
