# Third-Party Notices

`mileswang-skill` v0.3.0 is a clean-room implementation of Miles Wang's own routing, project-execution, content-creation, methodology, and semantic video-editing workflows.

No third-party Skill source code, prompt text, scripts, knowledge bases, media, model outputs, or private data are bundled in this release. Public projects below were inspected only to understand product structure and packaging conventions.

Runtime references such as `pdf:pdf` or `github:gh-fix-ci` are canonical names used in simulated routing fixtures. They do not bundle, relicense, or claim ownership of the referenced Skills. Availability and licensing remain with the independently installed provider.

## Architecture references

### HyperFrames

- Package: <https://www.npmjs.com/package/hyperframes>
- Pinned runtime version: `0.7.81`.
- License: Apache-2.0 according to the published npm package metadata.
- Use here: project-local transcription orchestration, browser-based checks,
  snapshots, preview, and rendering.
- Bundled material: none. The package, managed browser, fonts, and local Whisper
  model are downloaded into the user's own project/cache only after approval.
- Credentials: no Miles API, account, token, or private service is used.

### OpenAI Plugins

- Upstream: <https://github.com/openai/plugins>
- Documentation: <https://developers.openai.com/codex/plugins/build>
- Use here: official plugin manifest, marketplace, and directory conventions.
- Bundled material: none. Individual upstream plugins may have different licenses and terms.

### yichen-skills

- Upstream: <https://github.com/mcncarl/yichen-skills>
- License: <https://github.com/mcncarl/yichen-skills/blob/main/LICENSE>
- Use here: high-level observation that one branded repository can contain multiple narrow Skills.
- Bundled material: none. No prompts, scripts, documentation, assets, or branding were copied.

### dbskill

- Upstream: <https://github.com/dontbesilent2025/dbskill>
- Inspected baseline: `v2.18.8` at commit `7d05ba5691dff5de339f6e3b601369688907b22e`.
- License: <https://github.com/dontbesilent2025/dbskill/blob/7d05ba5691dff5de339f6e3b601369688907b22e/LICENSE>
- Use here: high-level observation of a router plus independent modules and release-contract concepts.
- Bundled material: none. `dbskill` is licensed under CC BY-NC 4.0; its content is not relicensed by this repository.

### Anthropic Skills

- Upstream: <https://github.com/anthropics/skills>
- Use here: high-level observation of self-contained Skill directories and progressive disclosure.
- Bundled material: none. The upstream repository contains components under different license terms; no upstream prompt, script, documentation, or asset was copied.

### Superpowers

- Upstream: <https://github.com/obra/superpowers>
- License: MIT at inspection time.
- Use here: high-level observation that workflow decisions should remain in narrow, independently triggered Skills rather than one giant entry prompt.
- Bundled material: none.

### Hugging Face Skills

- Upstream: <https://github.com/huggingface/skills>
- License: Apache-2.0 at inspection time.
- Use here: high-level observation of a multi-Skill repository that preserves individual capability boundaries and cross-agent compatibility.
- Bundled material: none.

## Future integrations

A future module that depends on third-party material must document its exact upstream URL, pinned version, license, modifications, distribution mode, and required attribution before it can be bundled. If those facts are missing or incompatible with this repository's distribution, the dependency must remain external.
