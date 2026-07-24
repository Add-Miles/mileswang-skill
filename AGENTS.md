# Repository Maintenance Rules

These instructions apply only to this repository. They do not replace a user's global or project-level `AGENTS.md`.

## Product boundary

`mileswang-skill` is one public brand, one marketplace entry, and one installable plugin containing narrow internal Skills.

- Keep `mileswang` as a thin router.
- Put project execution in `miles-project` and content work in `miles-content`.
- Add future capabilities as independent Skills under `plugins/mileswang-skill/skills/`.
- Do not add a placeholder capability before its real implementation, inputs, license, security boundary, and acceptance path exist.
- Do not copy or rename third-party Skill content and present it as Miles-owned work.

## Sources of truth

- `VERSION` is the release version authority.
- `plugins/mileswang-skill/.codex-plugin/plugin.json` is the installable plugin manifest.
- `.agents/plugins/marketplace.json` is the only public marketplace catalog for this repository.
- `plugins/mileswang-skill/skills/` contains the loadable Skill payload.
- `templates/AGENTS.md` is an optional portable template; it must not contain machine-specific paths or identities.
- Local `PROJECT.md` contains private requirement evidence and is intentionally ignored. Never link or publish it.

Keep the release version identical in `VERSION` and the plugin manifest. The marketplace must expose exactly one plugin named `mileswang-skill`.

## Before changing the repository

1. Check whether an installed, task-specific Skill applies and follow it when it does.
2. Read the real files in scope and state the one input-to-output change being made.
3. For a new capability, inspect existing mature implementations only after the requirement is clear. Stars are discovery signals, not proof of fit.
4. Verify ownership, license compatibility, maintenance state, security, and actual workflow fit before reusing anything.
5. Preserve unrelated user changes and keep one main cause hypothesis per modification.

If a request contains multiple independent tasks, assign one bounded task to each Agent. Do not let multiple Agents edit the same files without explicit coordination.

## Handoff gate

Every Agent handoff must include the minimum sufficient context:

1. the user's real objective and final deliverable;
2. current progress, verified facts, and remaining assumptions;
3. attempted and rejected approaches with reasons;
4. relevant files, paths, conventions, and source material;
5. scope, prohibited actions, permissions, and acceptance evidence.

Never send secrets or unrelated personal data. After another Agent returns, re-check its claims against the original goal and real files before accepting them.

## Integration gate for a new Skill

A new Skill may be bundled only when all of these are true:

1. It has one bounded trigger and does not swallow unrelated specialist tasks.
2. Its real input, target result, intended user, and acceptance evidence are explicit.
3. Miles owns the content, or its license permits this exact distribution and attribution is preserved.
4. It contains no credentials, account data, private absolute paths, private chats, or unauthorized media.
5. Positive, negative, and routing cases exist.
6. The real workflow has been exercised with representative input.

Use `python3 tools/new_skill.py <kebab-case-name> --description "..."` to create structure. The scaffold is not completion evidence.

## Change discipline

- One change should test one main cause hypothesis.
- Compare the same input before and after any behavior change.
- Do not add rules, retries, fields, models, or fallback layers without evidence that they improve the core result.
- After two failed fixes for the same issue, stop patching and re-check the problem, input, data flow, and acceptance criteria.
- Protect every verified release as a rollback baseline; never rewrite an existing release tag.
- Keep internal analysis detailed when needed, but keep user-facing output direct and task-centered.

## Required checks

Before claiming a release is ready:

1. Parse all JSON files.
2. Run `python3 tools/validate.py`.
3. Run `python3 -m unittest discover -s tests -p 'test_*.py'`.
4. Confirm every manifest path resolves inside the repository.
5. Confirm `PROJECT.md` is ignored and not tracked.
6. Scan tracked files for secrets, private absolute paths, account data, and unlicensed material.
7. Test a clean local marketplace install.
8. Exercise the three routing acceptance cases with fresh Agents and real representative inputs.
9. For a public release, verify the unauthenticated GitHub URL and the exact published commit.

Structural checks, installation, and public visibility are intermediate evidence. State workflow usefulness only at the level proven by real use.
