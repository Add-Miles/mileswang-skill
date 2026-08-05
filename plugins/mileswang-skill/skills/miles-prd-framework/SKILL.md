---
name: miles-prd-framework
description: "Extract lean writing frameworks from complete PRDs (link or text), then gap-fill a half-written PRD structure by demand type and business audience. Use when the user shares a PRD link or draft, asks to learn PRD structure, 梳理PRD框架, or 补全半成品PRD; do not use to invent full product specs without source material or to bypass internal-doc permissions."
---

# Miles PRD Framework

Learn **how a complete PRD is written**, then only **supplement structure** for a half draft. Prefer a short outline over a rewritten document.

## Primary path

```
Mode A — complete PRD (link preferred) → extract writing framework
Mode B — half draft + framework from A → structure gap list only
```

1. Detect mode from the user message.
2. For Mode A, open a readable link when the host can; on login/403/SSO failure, stop and ask for paste/export. Never bypass access control.
3. For Mode B, require a prior or co-supplied complete framework; do not invent a team template from empty context.
4. Classify demand type and primary readers before choosing section order (see [framework reference](references/framework.md)).
5. Return the compact templates below. Do not expand into a full PRD unless the user explicitly asks to draft body copy.

## Permission gate

| Allow | Forbid |
| --- | --- |
| Read user-supplied links that already resolve for this session | Bypass login, SSO, VPN, or 403 |
| Analyze pasted text, export, screenshot outline, or local draft | Edit company wiki/PRD systems without explicit local-file write request |
| Write analysis only into chat or a user-named local file | Publish internal PRD body to public repos |
| Mark missing sections as structure gaps | Fabricate product rules, metrics, or scope not supported by material |

## Mode A output (complete PRD)

```markdown
# Framework note · [title]

## Positioning
- Demand type:
- Business / readers:
- One line: who · problem · success

## Writing frame (source order)
1. Section — what this section persuades / how deep
2. …

## Writing habits for this class
- Order rationale
- What is core vs appendix
- Contrast to other demand types if clear

## Empty skeleton
Section titles only.

## Structure gaps
0–3 missing logical sections, or none.
```

## Mode B output (half draft)

```markdown
# Structure fill · [draft title]

## Reference
- Framework source: [complete PRD title]
- Type match: yes/no (if no, name the better type)

## Contrast table
| Framework expects | Draft | Action |

## Recommended outline
Mark [have] [add] [optional]

## What to write per new section (one line each)
```

## Demand-type centers (pick one, do not use a universal TOC)

| Type | Must clarify | Can stay light |
| --- | --- | --- |
| Feature / UX | problem → scene → path → rules → acceptance | heavy commercial thesis |
| Growth / funnel | hypothesis → audience → experiment → guardrails | pixel-perfect UI inventory |
| Transaction / risk | state machine → rule table → audit → rollback | lifestyle vision |
| Internal tools | roles → task flow → fields/states → efficiency | consumer marketing copy |
| Platform / API | caller scenarios → contract → quotas/errors → compat | single-surface UI prose |
| Ops config | config model → scope → priority → rollback | long product narrative |
| Pure experiment | hypothesis → split → window → decision rule | multi-year roadmap |
| Tech debt | cost of status quo → boundary → rollback → verify | stacks of user stories |

## Audience density

Infer who the doc mainly serves from section weight; when filling a draft, prioritize sections that unblock that review audience (biz/ops, design, eng, QA, data, compliance).

## Boundaries

- Framework over body text.
- No specialist rewrite of Figma, code, or experiment stats.
- When `mileswang` invokes this Skill, use the host-provided active Skill catalog as the only availability authority and keep the selected executor unchanged. Do not rediscover or replace the selected executor from disk folders, plugin caches, local inventories, or configuration files.

## Protect Miles personal information

Allow the public Miles brand, but keep non-brand contact details, private paths,
account identifiers, credentials, chats, and unpublished personal material out of
public artifacts, logs, errors, and Agent handoffs. Stop instead of exposing
protected values when a draft cannot be summarized safely.
