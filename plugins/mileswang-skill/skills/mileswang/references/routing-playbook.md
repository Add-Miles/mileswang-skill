# Routing Playbook

Use this reference only when the primary skill is not obvious.

## Decision table

| Request signal | Primary owner | Miles layer | Route boundary |
| --- | --- | --- | --- |
| Build, fix, restore, migrate, release, deploy, or materially change a project | Narrowest applicable engineering or platform skill | `miles-project` | Establish scope, authority, and real-path evidence before claiming completion. |
| Draft, script, post, title, article, or revision for an audience | Narrowest applicable platform or format skill, otherwise `miles-content` | `miles-content` | Preserve facts, find a real scene and conflict, and cut filler. |
| Browser, spreadsheet, image, video, document, API, or platform-specific operation | Matching specialist skill | Add a Miles layer only if the deliverable also meets its trigger | Do not make `mileswang` perform the specialist procedure. |
| Explanation, translation, lookup, or small factual answer | Direct answer or matching research skill | None by default | Do not force a project contract onto a simple request. |
| Two independent deliverables | One owner or agent per deliverable | Apply per task | Do not hide two tasks inside one vague execution plan. |

## Specialist discovery checklist

- Check the currently installed skill catalog before creating anything.
- Prefer an explicitly named and applicable skill.
- Prefer the narrowest skill with a real workflow over a broad brand router.
- For reusable project capabilities, inspect mature public implementations when network access and scope permit.
- Treat popularity as a discovery signal, not proof. Verify license, maintenance state, security, inputs, outputs, and fit before reuse.
- Keep external attribution and identity intact.

## Concrete routing examples

### Example: ambiguous deployment

Input:

> Deploy the newest version of our support dashboard.

Route:

1. Select the installed deployment skill as the domain executor.
2. Apply `miles-project` because “newest” and “deploy” require version authority and rollback evidence.
3. Stop before deployment if two plausible source versions remain.

### Example: verbose short-video draft

Input:

> Cut the filler from this short-video script and make the opening concrete.

Route:

1. Select a platform-specific script skill if one exists and applies.
2. Otherwise select `miles-content` directly.
3. Do not activate `miles-project`; the deliverable is a text revision, not a project mutation.

### Example: X browser operation

Input:

> Open X and collect the links from these five accounts.

Route:

1. Select the installed browser or X specialist.
2. Do not route to `miles-content` merely because the source is a social platform.
3. Add `miles-project` only if the user is building or changing a reusable collection system.

## Handoff check

Before delegating, include all of the following:

- the user's real goal and final deliverable;
- verified facts and remaining assumptions;
- attempted and rejected approaches with reasons;
- accessible source files, inputs, and project conventions;
- current scope, prohibitions, permissions, and acceptance evidence.

After delegation, inspect the original inputs and verify the result yourself. A structured report or a completion claim is not evidence by itself.
