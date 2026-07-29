---
name: mileswang
description: "Route explicit Miles Wang workflow requests to the narrowest active skill and apply Miles's first-principles guardrails without replacing specialist expertise. Use when the user invokes mileswang or asks to handle a project or creator-content request in the Miles workflow; do not use as a substitute for a more specific active skill."
---

# Mileswang System Router

Act as a thin entry and router for Miles-owned and independently maintained
Skills. Do not turn this skill into an all-purpose executor.

## Choose the interaction mode

Read the complete current conversation before asking for input.

- **First-use onboarding:** when the user explicitly asks how to begin or says
  this is their first use, explain what they can submit, how one executor is
  selected, what concrete result they may receive, and ask them to send one
  real task. Do not expose the full catalog or make them memorize commands.
- **Pre-task routing:** when the conversation contains a current task but no
  completed Skill result, route that task using the rules below.
- **Post-task navigation:** when a Skill has produced a concrete result in this
  conversation and the user asks what to do next, extract that result and the
  user's latest feedback. Select only one next executor. If the user already
  chose an applicable next step, honor it. If two materially different routes
  remain tied, ask one deciding question and stop.

Read [system behavior](references/system-behavior.md) for onboarding wording,
post-task navigation, and capability states. Do not precompute a fixed chain of
Skills; every next route must depend on the actual current result.

Read and apply the [public privacy contract](references/privacy-contract.md)
before producing any public artifact, final response, log, error, or Agent
handoff. The public brand is allowed; non-brand Miles personal information is
not.

## Route the request

1. State the user's single primary deliverable in one sentence.
2. Read the host-provided **active Skill catalog** before planning, answering, or acting. It is the only authority for what this session can execute.
3. Honor an explicitly named Skill only when its exact canonical name is active and its workflow fits the requested operation.
4. Select one narrowest Skill that owns the core operation.
5. Load only the Miles module needed for the request:
   - Use [miles-project](../miles-project/SKILL.md) for building, changing, repairing, restoring, migrating, publishing, or deploying a project.
   - Use [miles-content](../miles-content/SKILL.md) for creating, diagnosing, or revising creator-facing content.
   - Use [miles-x-methodology](../miles-x-methodology/SKILL.md) when real X post material must be analyzed into evidence-labeled first principles, methodology, transferable actions, and verification boundaries.
   - Use [miles-video-editing](../miles-video-editing/SKILL.md) when one supplied talking-head video must become a V10-style semantic edit with a real checked and approved render path.
   - Use [miles-ai-video](../miles-ai-video/SKILL.md) for planning, adapting, or reviewing AI-assisted short videos and demo videos from verified source material.
   - Use [miles-update](../miles-update/SKILL.md) when the user explicitly asks to check or install the latest stable `mileswang-skill` release.
   - Use neither when the request is a direct question or belongs entirely to another specialist.

Read the [routing playbook](references/routing-playbook.md) only when ownership is unclear, multiple tasks are mixed together, or a specialist skill must be combined with a Miles module.

## Keep capability ownership visible

Use the bundled [capability map](references/capability-map.json) only to explain
the system's released Miles-owned leaves and future candidates. It is not an
availability catalog.

- `released-owned` means this plugin contains the leaf and its integration
  contract passes.
- `candidate-owned` means the branch contains and contract-tests the leaf, but
  real-session usefulness or user acceptance is still missing; do not call it
  released.
- `external-runtime` means an independently maintained Skill may be delegated
  to only when its exact canonical name is in the current active Skill catalog.
- `future-candidate` is a backlog hypothesis, never an executor.

Never route to a future candidate. A `candidate-owned` leaf can be exercised for
acceptance on its implementation branch but must not be presented as a stable
release. Never claim an external Skill is available
because it appears in the capability map, on disk, or in another session.

## Resolve availability explicitly

Determine one route decision before execution:

- `internal`: the executor is an active bundled Miles leaf.
- `external-available`: the executor is an active Skill supplied independently outside this plugin.
- `unavailable`: the requested Skill is not active in this session, even if a disk directory or cache exists.
- `ambiguous`: two or more active candidates are equally plausible, or multiple host entries expose the same canonical name without a unique callable identity.

Keep the decision fields conceptually separate:

- **executor:** the exact canonical Skill name that performs the core operation, such as `pdf:pdf` or `github:gh-fix-ci`;
- **Miles layers:** always empty for an `internal` route; optional bundled Miles governance or analysis around an external executor, never a duplicate of the executor. Use `miles-x-methodology` around a browser or research executor only when that executor must first acquire the real source material for the requested X analysis;
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
- Add `miles-x-methodology` around an external acquisition executor only for URL-only X methodology requests; after acquisition it analyzes the returned evidence and does not replace the acquisition executor.
- Keep `miles-video-editing` as the internal method owner. Its default transcription and render path is the pinned project-local public toolchain; only a user-selected active external executor retains a separate active-catalog identity.
- Do not rename, copy, paraphrase, or present a third-party skill as a Miles-owned capability.
- Do not invent an internal module for a capability that has no real implementation, license basis, input, and acceptance path.
- Calling a Skill supplied independently outside this plugin is delegation, not redistribution. Never copy its prompt, code, assets, local data, or credentials into this plugin.

## Split genuinely independent tasks

When one request contains multiple independently verifiable deliverables, assign one owner or agent to each task. Give every handoff the minimum sufficient context: the real goal, verified and unverified state, rejected approaches, relevant inputs and conventions, scope and prohibitions, and acceptance evidence. Recheck the receiving agent's result against the original inputs before adopting it.

## Report the route briefly

Name the exact selected executor and any Miles governance layer in one short sentence. Then perform the work. For `unavailable` or `ambiguous`, report the status and stop for the one required user action. Do not expose a long routing analysis unless the route is blocked or the user asks for it.
