---
name: miles-video-editing
description: "Turn one supplied talking-head video into a reviewable V10-style semantic edit with timestamped captions, explanatory cards, micro-effects, spatial avoidance, and a verified vertical MP4. Use when a user asks Miles to AI-edit or package spoken footage; do not use for generative video, multi-camera NLE work, publishing, or a render without final preview approval."
---

# Miles Video Editing

Turn one real source video into one semantic, reviewable candidate. The visual
system must explain the speech; repeating subtitles in decorative boxes is not
completion.

## Use the public local toolchain

This Miles Skill owns the V10 method, portable workspace, storyboard contract,
composition builder, spatial rules, and acceptance. A user needs only this
plugin plus public local system prerequisites; they do not need another Skill,
Miles API, Miles credentials, or a Miles-hosted service.

Use the host-provided active Skill catalog as the only availability authority
when the user explicitly delegates an operation to another Skill. Keep the
catalog decision and keep the selected executor unchanged. Do not rediscover or replace the selected executor
from disk folders, caches, inventories, or configuration. The default path does
not delegate: it installs the pinned Apache-2.0 `hyperframes@0.7.81` npm package
inside the current video project and forces local Whisper transcription.

Never infer a transcript, media asset, successful check, or successful render.

Read [the V10 contract](references/v10-contract.md) before authoring the
storyboard and [the dependency contract](references/dependencies.md) before any
setup or render operation.

## Create an isolated project

Require one readable video with a video stream and audible primary speech. Run
the non-mutating environment check first:

```bash
python3 <SKILL_DIR>/scripts/video_workspace.py preflight --input <video> --json
```

Preflight never installs, downloads, or renders. A blocker stops the workflow.
When ready, initialize a new project outside the Skill directory:

```bash
python3 <SKILL_DIR>/scripts/video_workspace.py init \
  --input <video> --project-dir <new-project-dir>
```

The source is copied into `source/` and never overwritten. All manifest paths
are relative and must resolve inside the project.

With explicit approval for network and disk changes, install the project-local
public toolchain and pinned browser:

```bash
python3 <SKILL_DIR>/scripts/video_workspace.py setup \
  --project-dir <project-dir>
```

Setup installs only into `work/toolchain/`. It never reads an API key or writes
to the Skill package.

## Obtain evidence and author the storyboard

Transcribe the copied source locally:

```bash
python3 <SKILL_DIR>/scripts/video_workspace.py transcribe \
  --project-dir <project-dir> --language zh
```

This forces local Whisper and stores SRT at `work/transcript.srt`. Inspect and
correct the result against the real audio before authoring semantic beats; do
not publish the transcript with this Skill.

Create `work/spec/storyboard.json` from
[the public schema](references/storyboard.schema.json). Each semantic beat must
state the spoken claim it explains, its time range, one visual treatment, and
why that treatment adds information. Mark required real media as `missing`
until actually supplied or reconstructed from verified evidence.

Validate before building:

```bash
python3 <SKILL_DIR>/scripts/video_workspace.py validate \
  --project-dir <project-dir>
```

Missing media, transcript mismatch, out-of-range timing, duplicate IDs,
same-lane overlap, or unsafe lower-screen overlays block the build.

## Build and check the composition

Generate the portable HyperFrames project:

```bash
python3 <SKILL_DIR>/scripts/video_workspace.py build \
  --project-dir <project-dir>
```

The builder uses deterministic finite WAAPI animation and does not bundle GSAP,
private fonts, remote scripts, Miles media, or machine-specific paths.

From `work/composition/`, use the project-local pinned CLI:

```bash
npm install --ignore-scripts --no-audit --no-fund
npx hyperframes check --strict --snapshots
npx hyperframes preview
```

Package, browser, font, and model setup may use the public npm, Google Fonts, or
Hugging Face endpoints; perform them only after explicit user approval. None is
a Miles API. A passing check is not render approval. Show the final Studio
preview and wait for approval.

## Render and verify

After preview approval:

```bash
npx hyperframes render --quality high --output ../../outputs/candidate.mp4
python3 <SKILL_DIR>/scripts/video_workspace.py verify \
  --project-dir <project-dir> --output outputs/candidate.mp4 --json
```

Verify a real non-empty H.264/AAC 1080x1920 MP4, duration, frame rate, audio,
and snapshots. Call it a `candidate` until semantic timing, explanatory value,
caption readability, and spatial crowding pass human review. Automated checks
cannot promote this Skill from candidate to released-owned.

## Protect Miles personal information

Allow public Miles branding, but remove non-brand contact details, private
paths, account identifiers, private chats, and unnecessary face, voice, device,
location, or source-media metadata from previews, renders, logs, and handoffs.
Keep required private source media local and stop before any unapproved upload
or public export.
