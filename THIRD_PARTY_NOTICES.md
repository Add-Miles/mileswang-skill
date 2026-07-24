# Third-Party Notices

`mileswang-skill` v0.1 is a clean-room implementation of Miles Wang's own project-execution and content-creation workflows.

No third-party Skill source code, prompt text, scripts, knowledge bases, media, model outputs, or private data are bundled in this release. Public projects below were inspected only to understand product structure and packaging conventions.

## Architecture references

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
- License: <https://github.com/dontbesilent2025/dbskill/blob/main/LICENSE>
- Use here: high-level observation of a router plus independent modules.
- Bundled material: none. `dbskill` is licensed under CC BY-NC 4.0; its content is not relicensed by this repository.

## Future integrations

A future module that depends on third-party material must document its exact upstream URL, pinned version, license, modifications, distribution mode, and required attribution before it can be bundled. If those facts are missing or incompatible with this repository's distribution, the dependency must remain external.
