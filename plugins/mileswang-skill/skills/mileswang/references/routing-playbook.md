# Routing Playbook

Use this reference only when the primary skill is not obvious.

## Decision table

| Request signal | Primary owner | Miles layer | Route boundary |
| --- | --- | --- | --- |
| Build, fix, restore, migrate, release, deploy, or materially change a project | Narrowest applicable engineering or platform skill | `miles-project` | Establish scope, authority, and real-path evidence before claiming completion. |
| Draft, script, post, title, article, or revision for an audience | Narrowest applicable platform or format skill, otherwise `miles-content` | `miles-content` | Preserve facts, find a real scene and conflict, and cut filler. |
| Analyze supplied X material into first principles, methodology, transfer, and claim boundaries | `miles-x-methodology` | None | Use only the supplied and actually read evidence. |
| Analyze an X URL whose content has not been retrieved | Matching active browser or research Skill | `miles-x-methodology` | The external executor acquires the source; the Miles layer analyzes only returned evidence. |
| Browser, spreadsheet, image, video, document, API, or platform-specific operation | Matching specialist skill | Add a Miles layer only if the deliverable also meets its trigger | Do not make `mileswang` perform the specialist procedure. |
| Explanation, translation, lookup, or small factual answer | Direct answer or matching research skill | None by default | Do not force a project contract onto a simple request. |
| Two independent deliverables | One owner or agent per deliverable | Apply per task | Do not hide two tasks inside one vague execution plan. |

## Specialist discovery checklist

- Treat the current session's active Skill catalog as the availability authority. Do not infer availability from disk folders, plugin caches, or another session.
- Prefer an explicitly named and applicable Skill only when its exact canonical name is active.
- Prefer the narrowest skill with a real workflow over a broad brand router.
- For reusable project capabilities, inspect mature public implementations when network access and scope permit.
- Treat popularity as a discovery signal, not proof. Verify license, maintenance state, security, inputs, outputs, and fit before reuse.
- Keep external attribution and identity intact.

## Runtime route contract

| Status | Executor | Miles layers | Required behavior |
| --- | --- | --- | --- |
| `internal` | Active `miles-project` or `miles-content` | None | Execute the bundled leaf. |
| `external-available` | Exact active canonical name | Optional, separate from executor | Delegate the domain operation and preserve external identity. |
| `unavailable` | None | None | Name the unavailable request and do not silently replace it. |
| `ambiguous` | None | None | Name the tied candidates and ask one deciding question. |

Canonical names may be unnamespaced (`miles-content`) or namespaced (`pdf:pdf`, `github:gh-fix-ci`). Preserve them exactly as the host exposes them.

Disk presence is not session availability. A local directory, bridge, or cache entry that is absent from the active catalog must route as `unavailable`.

If multiple active catalog entries expose the same canonical name and the host does not provide a unique callable identity, treat that name as a collision. Return `ambiguous` and stop; do not select by provider order, path order, or cache order. If the host does expose unique callable identities, preserve and use that exact host identity.

## Concrete routing examples

### Example: ambiguous deployment

Input:

> Deploy the newest version of our support dashboard.

Route:

1. Select the applicable deployment Skill from the active catalog as the domain executor.
2. Apply `miles-project` because “newest” and “deploy” require version authority and rollback evidence.
3. Stop before deployment if two plausible source versions remain.

Decision shape: `external-available`; executor is the exact deployment Skill name; Miles layer is `miles-project`.

### Example: verbose short-video draft

Input:

> Cut the filler from this short-video script and make the opening concrete.

Route:

1. Select a platform-specific script Skill if it is active and applies.
2. Otherwise select `miles-content` directly.
3. Do not activate `miles-project`; the deliverable is a text revision, not a project mutation.

### Example: X browser operation

Input:

> Open X and collect the links from these five accounts.

Route:

1. Select the applicable browser or X specialist from the active catalog.
2. Do not route to `miles-content` merely because the source is a social platform.
3. Add `miles-project` only if the user is building or changing a reusable collection system.

### Example: X methodology from supplied text

Input contains the post text and asks what method Miles can transfer.

1. Select `miles-x-methodology` as the internal executor.
2. Do not activate a browser Skill because the required source is already present.
3. Exclude comments and label unsupported claims and inference explicitly.

### Example: X methodology from URL only

Input contains only an X URL and asks for methodology analysis.

1. Select the applicable active browser or research Skill as the external
   acquisition executor.
2. Add `miles-x-methodology` as the analysis layer.
3. If acquisition fails or omits essential media or context, report the missing
   evidence instead of producing a complete analysis.

### Example: explicit external Skill

Input:

> Use `pdf:pdf` to edit this PDF.

Route:

1. Confirm `pdf:pdf` is in the active catalog and the operation is a PDF edit.
2. Return `external-available` with executor `pdf:pdf` and no Miles layer.
3. Delegate the work without copying or summarizing the external Skill into Miles-owned files.

### Example: named but unavailable

Input:

> Use `vendor:missing-skill` for this task.

Route:

1. If the exact name is absent from the active catalog, return `unavailable`.
2. Do not treat a cache or filesystem match as availability.
3. Do not silently route to `miles-project` or `miles-content`.

### Example: explicit but incompatible

Input:

> Use `pdf:pdf` to deploy my website.

Route:

1. Do not select `pdf:pdf`; explicit naming does not override task fit.
2. Select an active deployment Skill if one clearly owns the operation and add `miles-project` as governance.
3. If two deployment Skills remain equally suitable, return `ambiguous` and ask one deciding question.

### Example: duplicate canonical name

Input:

> Use `general-video` for this video task.

Route:

1. The active catalog exposes two entries named `general-video` but no distinct callable identities.
2. Return `ambiguous` with `general-video` as the colliding candidate.
3. Do not choose one from its filesystem location or provider order; request the one host-level distinction needed to proceed.

## Handoff check

Before delegating, include all of the following:

- the user's real goal and final deliverable;
- verified facts and remaining assumptions;
- attempted and rejected approaches with reasons;
- accessible source files, inputs, and project conventions;
- current scope, prohibitions, permissions, and acceptance evidence.

After delegation, inspect the original inputs and verify the result yourself. A structured report or a completion claim is not evidence by itself.
