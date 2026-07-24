---
name: mileswang
description: "Route explicit Miles Wang workflow requests to the narrowest available skill and apply Miles's first-principles guardrails without replacing specialist expertise. Use when the user invokes mileswang or asks to handle a project or creator-content request in the Miles workflow; do not use as a substitute for a more specific installed skill."
---

# Mileswang Router

Act as a thin router. Do not turn this skill into an all-purpose executor.

## Route the request

1. State the user's single primary deliverable in one sentence.
2. Inspect the installed skills before planning, answering, or acting.
3. Honor an explicitly named skill when it applies.
4. Select the narrowest skill that owns the core operation.
5. Load only the Miles module needed for the request:
   - Use [miles-project](../miles-project/SKILL.md) for building, changing, repairing, restoring, migrating, publishing, or deploying a project.
   - Use [miles-content](../miles-content/SKILL.md) for creating, diagnosing, or revising creator-facing content.
   - Use neither when the request is a direct question or belongs entirely to another specialist.

Read the [routing playbook](references/routing-playbook.md) only when ownership is unclear, multiple tasks are mixed together, or a specialist skill must be combined with a Miles module.

## Keep specialist ownership intact

- Let a specialist skill control its domain-specific procedure, tools, and validation.
- Add `miles-project` as a governance layer only when the work changes a project, has an ambiguous target, or involves restoration, migration, publication, or deployment.
- Add `miles-content` only when the deliverable itself is creator-facing content.
- Do not rename, copy, paraphrase, or present a third-party skill as a Miles-owned capability.
- Do not invent an internal module for a capability that has no real implementation, license basis, input, and acceptance path.

## Split genuinely independent tasks

When one request contains multiple independently verifiable deliverables, assign one owner or agent to each task. Give every handoff the minimum sufficient context: the real goal, verified and unverified state, rejected approaches, relevant inputs and conventions, scope and prohibitions, and acceptance evidence. Recheck the receiving agent's result against the original inputs before adopting it.

## Report the route briefly

Name the selected executor and any Miles governance layer in one short sentence. Then perform the work. Do not expose a long routing analysis unless the route is blocked or the user asks for it.
