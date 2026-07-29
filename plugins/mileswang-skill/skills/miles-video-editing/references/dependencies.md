# Dependency contract

## Bundled and Miles-owned

- `video_workspace.py`: Python 3.10+ standard-library workspace, validation,
  composition generation, and output verification.
- `storyboard.schema.json` and the V10 method rules.
- No executable, model, browser, font, video, transcript, screenshot, GSAP
  bundle, credential, or private path is distributed.

## Independently installed executors

- Timestamped transcription: exact active `media-use` or `hyperframes-media`.
- Composition checking and rendering: exact active `hyperframes` and
  `hyperframes-cli`.
- External evidence/media acquisition: an applicable active specialist, only
  with authorization.

The active catalog is the availability authority. Never claim that a cache or
disk directory makes one of these available.

## System prerequisites

- Python 3.10 or newer.
- Node.js 22 or newer plus npm/npx.
- FFmpeg and ffprobe on `PATH`.
- Project-local `hyperframes@0.7.81` candidate pin. This becomes the stable pin
  only after the protected V10 same-input comparison passes.
- A HyperFrames-managed browser and transcription model may require a first-use
  download. Setup must be explicit; ordinary preflight must remain offline and
  non-mutating.

Missing prerequisites return `blocked` or `setup_required`. They never trigger
silent installation or a placeholder output.
