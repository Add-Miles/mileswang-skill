---
name: miles-prd-framework
description: >-
  Extract portable writing frameworks and module I/O contracts from complete
  PRDs (link or text), then structure-fill half drafts without topic-polluted
  skeletons. Use when the user shares a PRD, asks to 梳理PRD框架, learn
  transferable structure, 模块契约, or 补全半成品PRD; do not invent full product
  specs without source material or bypass internal-doc permissions.
---

# Miles PRD Framework

Goal: **portable writing frame + module contracts**, not a retelling of one topic’s TOC.

Split always:

| Layer | Answers |
| --- | --- |
| Portable frame | How docs of this **demand type** should be written |
| Module contracts | Duty, inputs, process, outputs, handoff, exception, acceptance per module |
| Current mapping | How **this** document’s real modules fill those slots |

Prefer short structure over rewritten body copy.

## Primary path

```
Mode A — complete PRD → abstraction process → portable skeleton → contracts → mapping
Mode B — half draft + Mode A frame → structure contrast with contract/interface gaps
```

1. Detect mode from the user message.
2. Mode A: open readable links; on login/403/SSO failure, stop and ask for paste/export. Never bypass access control.
3. Mode B: require a prior or co-supplied Mode A frame; do not invent a team template from empty context.
4. Classify **demand type** and **primary readers** before centering modules (see [framework.md](references/framework.md)).
5. Do **not** drop current-topic tech module names into the empty skeleton; put them only under Current document mapping.

## Permission gate

| Allow | Forbid |
| --- | --- |
| Read user-supplied links that already resolve | Bypass login, SSO, VPN, or 403 |
| Analyze paste, export, outline, local draft | Edit company wiki/PRD without explicit local path |
| Write analysis to chat or user-named local file | Publish internal PRD body to public repos |
| Mark structure gaps and evidence gaps separately | Fabricate rules, metrics, or scope unsupported by source |

## Abstraction process (Mode A must show)

Before final results, show these steps (brief, not essay):

1. Rewrite each source section as the **question it answers** (not copied title).
2. Name the **review decision** it supports and **primary readers**.
3. Extract **end-to-end module chain**: upstream input → process/decision → output → downstream use.
4. Replace topic nouns with **generic slots** → portable empty skeleton.
5. Map slots back to **this document’s real modules**, keeping duty and handoffs.
6. Audit: structure gap vs evidence/asset gap (never merge the two).

## Demand-type centers (pick one; no universal TOC)

After type is chosen, center module contracts on that spine:

| Type | Center |
| --- | --- |
| Feature / UX | problem → scene → path → rules → acceptance |
| Growth / experiment | hypothesis → audience → experiment → guardrails → decision window |
| Transaction / risk | rules → audit → compliance → rollback → monitors |
| Internal tools | roles → task flow → fields → actions → efficiency |
| Platform / API | caller scenarios → contract → quotas/errors → compatibility |
| Ops config | config model → scope → priority → conflict → rollback |
| Pure experiment | hypothesis → split → window → decision rule |
| Tech debt | status-quo cost → boundary → rollback → verify |

## Module contract (required per module)

Module **titles alone are not a requirement**. For every system/process unit (even when names look similar, **do not merge** them), force all fields:

| Field | Must answer | Expected yield |
| --- | --- | --- |
| Duty | What problem does this module own alone? | Clear responsibility boundary |
| Upstream input | From which module? What fields/objects/conditions? | Sources and required fields |
| Process / judgment | What transform, detect, compute, or decide? | Structural process description |
| Output | What fields/results to downstream? Meaning of each? | Outputs, meaning, status |
| Handoff | When emit, how long, when stop/revoke? | Trigger, duration, stop |
| Downstream use | How does each important result get used? | Triggered judgment or action |
| Exception | Missing, low confidence, conflict, stale, fail? | Conservative or fallback path |
| Acceptance evidence | How prove the module and handoff work? | Test, log, screenshot, sample |

## Module interface table (Mode A and Mode B)

Answer: what the upstream gives the downstream, and what the downstream does with it.

| Upstream | Upstream output | Downstream | Downstream use | Handoff condition |
| --- | --- | --- | --- | --- |
| Module A | result/field A | Module B | judgment or second process | after condition, while valid |
| … | … | … | … | … |

## Frame vs instance (hard rule)

- **Empty skeleton / portable frame**: only roles and structure slots — **no** current-topic tech module names, product object names, or action brand names.
- **Current document mapping**: real module names + full contracts/handoffs for this topic.
- Portable frame = how this class of PRD is written; mapping = how this theme implements the chain.

## Structure gaps vs evidence gaps

| Kind | Report when | Do not report when |
| --- | --- | --- |
| **Structure gap** | Missing goal, duty, I/O, handoff, exception, acceptance, or interface that **blocks review/decision** | “Could be more detailed” without decision impact |
| **Evidence / asset gap** | Image placeholder, missing flowchart, empty table, missing video/sample data | Structure text is present |

When suggesting assets, reuse the source’s table style, image viewpoint, annotation style, and naming templates.

## Mode A output template

```markdown
# Framework note · [title]

## Positioning
- Demand type:
- Primary readers:
- One line: who · problem · success

## Abstraction process
1. Section questions…
2. Decisions & readers…
3. Module chain (names may appear here as analysis, not as portable skeleton)…
4. Slot replacement…
5. Map-back notes…
6. Gap audit notes…

## Writing frame (source order)
1. Section — question answered — decision supported
2. …

## Empty skeleton (portable; no current-topic module names)
- …

## Module contracts
### [Portable slot or temporary label]
- Duty / Input / Process / Output / Handoff / Downstream / Exception / Acceptance
(repeat per module; similar names stay separate if roles differ)

## Module interface table
| Upstream | Upstream output | Downstream | Downstream use | Handoff condition |

## Current document mapping
| Portable slot | Real module in source | Duty (short) | Key I/O handoff |

## Structure gaps
Only decision-blocking structure/interface issues (0–N).

## Evidence / asset gaps
Images, flows, attachments, samples; keep original template habits.
```

## Mode B output template

Base only on a Mode A frame from the same conversation or co-supplied complete PRD frame.

```markdown
# Structure fill · [draft title]

## Reference
- Framework source:
- Demand type match: yes/no (if no → better type)

## Contrast (sections + contracts + interfaces)
| Framework expects | Draft | Status: have / thin / add / optional / unclear | Action |

## Recommended outline
[have] [add] [optional] …

## Module contract gaps
Modules missing duty/I/O/handoff/exception/acceptance

## Interface gaps
Missing or unclear upstream→downstream transfers

## What to write (one line per add)
Structure prompts only — not full product rewrite.
```

## Verification reminder (not portable skeleton)

When the source is multi-module (e.g. perception pipeline), keep **similar-looking modules separate** if duties differ (e.g. on-device VLM vs cloud VLM vs human ops cabin). Instance mapping may show the real chain; empty skeleton must not bake in those product names.

## Boundaries

- Framework and contracts first; no full PRD rewrite unless asked.
- No specialist expansion of Figma, code, or experiment math beyond structure.
- When `mileswang` invokes this Skill, use the host-provided active Skill catalog as the only availability authority and keep the selected executor unchanged. Do not rediscover or replace the selected executor from disk folders, plugin caches, local inventories, or configuration files.

## Protect Miles personal information

Allow the public Miles brand, but keep non-brand contact details, private paths,
account identifiers, credentials, chats, and unpublished personal material out of
public artifacts, logs, errors, and Agent handoffs. Stop instead of exposing
protected values when a draft cannot be summarized safely.
