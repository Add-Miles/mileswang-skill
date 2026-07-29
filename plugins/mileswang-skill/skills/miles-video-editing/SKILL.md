---
name: miles-video-editing
description: "Turn one supplied talking-head video into a reviewable V10-style semantic edit with timestamped captions, explanatory cards, micro-effects, spatial avoidance, and a verified vertical MP4. Use when a user asks Miles to AI-edit or package spoken footage; do not use for generative video, multi-camera NLE work, publishing, or a render without final preview approval."
---

# Miles Video Editing

Turn one real source video into one semantic, reviewable candidate. The visual
system must explain the speech; repeating subtitles in decorative boxes is not
completion.

## Route the real executors

This Miles Skill owns the V10 method, portable workspace, storyboard contract,
composition builder, spatial rules, and acceptance. It does not rename or copy
external executors.

Use the host-provided active Skill catalog as the only availability authority
and keep the selected executor unchanged. Do not rediscover or replace the selected executor from disk folders, caches, inventories, or configuration.

- Use the active `media-use` or `hyperframes-media` executor for timestamped
  transcription. Preserve the exact selected canonical name.
- Use the active `hyperframes` and `hyperframes-cli` workflows to check,
  preview, snapshot, and render the generated composition.
- If a required executor is not active, stop and name it. Disk presence is not
  session availability.
- Never infer a transcript, media asset, or successful render.

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

## Obtain evidence and author the storyboard

Transcribe the copied source through the selected active executor. Store SRT at
`work/transcript.srt`; do not publish the transcript with this Skill.

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

From `work/composition/`, use the selected HyperFrames executors:

```bash
npm install
npx hyperframes check --strict --snapshots
npx hyperframes preview
```

`npm install` and browser/model setup change the machine and may use the
network; perform them only after explicit user approval. A passing check is not
render approval. Show the final Studio preview and wait for approval.

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
