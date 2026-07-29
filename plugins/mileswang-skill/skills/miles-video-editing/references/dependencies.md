# Dependency contract

## Bundled and Miles-owned

- `video_workspace.py`: Python 3.10+ standard-library workspace, validation,
  composition generation, and output verification.
- `storyboard.schema.json` and the V10 method rules.
- No executable, model, browser, font, video, transcript, screenshot, GSAP
  bundle, credential, or private path is distributed.

## Public local toolchain

- Project-local `hyperframes@0.7.81` from the public npm registry, pinned in the
  generated project. Its CLI provides local Whisper transcription, browser
  management, checking, preview, snapshots, and rendering.
- No separately installed HyperFrames or media Skill is required.
- External evidence/media acquisition remains optional and requires explicit
  authorization when a storyboard genuinely needs it.

## System prerequisites

- Python 3.10 or newer.
- Node.js 22 or newer plus npm/npx.
- FFmpeg and ffprobe on `PATH`.
- Project-local `hyperframes@0.7.81` candidate pin. This becomes the stable pin
  only after the protected V10 same-input comparison passes.
- A HyperFrames-managed browser and local Whisper model may require a first-use
  public download. Setup must be explicit; ordinary preflight remains offline
  and non-mutating.

This workflow does not call, proxy, read, or require a Miles API, key, account,
or hosted service. Local rendering and local Whisper need no API key. Public
package/model downloads are network access, but they are not author APIs.

Missing prerequisites return `blocked` or `setup_required`. They never trigger
silent installation or a placeholder output.
