---
name: mileswang
description: "Route explicit Miles Wang workflow requests to the narrowest active skill and apply Miles's first-principles guardrails without replacing specialist expertise. Use when the user invokes mileswang or asks to handle a project or creator-content request in the Miles workflow; do not use as a substitute for a more specific active skill."
---

# Mileswang Router

Act as a thin router. Do not turn this skill into an all-purpose executor.

## Route the request

1. State the user's single primary deliverable in one sentence.
2. Read the host-provided **active Skill catalog** before planning, answering, or acting. It is the only authority for what this session can execute.
3. Honor an explicitly named Skill only when its exact canonical name is active and its workflow fits the requested operation.
4. Select one narrowest Skill that owns the core operation.
5. Load only the Miles module needed for the request:
   - Use [miles-project](../miles-project/SKILL.md) for building, changing, repairing, restoring, migrating, publishing, or deploying a project.
   - Use [miles-content](../miles-content/SKILL.md) for creating, diagnosing, or revising creator-facing content.
   - Use [miles-ai-video](../miles-ai-video/SKILL.md) for planning, adapting, or reviewing AI-assisted short videos and demo videos from verified source material.
   - Use neither when the request is a direct question or belongs entirely to another specialist.

Read the [routing playbook](references/routing-playbook.md) only when ownership is unclear, multiple tasks are mixed together, or a specialist skill must be combined with a Miles module.

## Resolve availability explicitly

Determine one route decision before execution:

- `internal`: the executor is an active bundled Miles leaf.
- `external-available`: the executor is an active Skill supplied independently outside this plugin.
- `unavailable`: the requested Skill is not active in this session, even if a disk directory or cache exists.
- `ambiguous`: two or more active candidates are equally plausible, or multiple host entries expose the same canonical name without a unique callable identity.

Keep the decision fields conceptually separate:

- **executor:** the exact canonical Skill name that performs the core operation, such as `pdf:pdf` or `github:gh-fix-ci`;
- **Miles layers:** always empty for an `internal` route; optional `miles-project` or `miles-content` governance only around an external executor, never a duplicate of the executor;
- **reason:** one concrete sentence tied to the requested operation.

For `unavailable` or `ambiguous`, both executor and Miles layers must be empty. Keep an unavailable requested name only in the reason, and keep tied active names only as candidates; neither state performs an operation.

Simple direct answers bypass Skill routing. Do not expose the full decision schema unless the route is blocked, ambiguous, or the user asks for it.

Do not scan `~/.codex/skills`, `~/.agents/skills`, `~/.claude/skills`, plugin caches, or configuration files to claim availability. Disk presence is not session availability.

## Handle explicit names and failures

- Preserve the full canonical name and third-party identity. Do not shorten `pdf:pdf` to `pdf` or turn an external name into `miles-*`.
- If an explicitly named Skill is active but does not fit the operation, say why and choose the actually applicable active Skill or ask one deciding question.
- If the named Skill is unavailable, report that fact and do not silently substitute another executor.
- If multiple active entries expose the same canonical name and the host supplies no unique callable identity, return `ambiguous`; never choose by disk path, provider order, or cache order.
- If equally suitable active Skills remain, return `ambiguous` and ask only the question that separates them.
- If the catalog lists an executor but loading or execution fails, report the failure. Do not fall back to an example result or pretend the Miles layer performed the specialist operation.
- If a bundled Miles leaf is missing from the active catalog, treat the plugin as incomplete and stop.

## Keep specialist ownership intact

- Let a specialist skill control its domain-specific procedure, tools, and validation.
- Once an executor is selected, a Miles layer must not rediscover or replace it.
- Add `miles-project` as a governance layer only when the work changes a project, has an ambiguous target, or involves restoration, migration, publication, or deployment.
- Add `miles-content` only when the deliverable itself is creator-facing content.
- Do not rename, copy, paraphrase, or present a third-party skill as a Miles-owned capability.
- Do not invent an internal module for a capability that has no real implementation, license basis, input, and acceptance path.
- Calling a Skill supplied independently outside this plugin is delegation, not redistribution. Never copy its prompt, code, assets, local data, or credentials into this plugin.

## Split genuinely independent tasks

When one request contains multiple independently verifiable deliverables, assign one owner or agent to each task. Give every handoff the minimum sufficient context: the real goal, verified and unverified state, rejected approaches, relevant inputs and conventions, scope and prohibitions, and acceptance evidence. Recheck the receiving agent's result against the original inputs before adopting it.

## Report the route briefly

Name the exact selected executor and any Miles governance layer in one short sentence. Then perform the work. For `unavailable` or `ambiguous`, report the status and stop for the one required user action. Do not expose a long routing analysis unless the route is blocked or the user asks for it.
