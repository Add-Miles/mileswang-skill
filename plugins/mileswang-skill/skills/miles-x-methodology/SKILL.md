---
name: miles-x-methodology
description: "Analyze an X post or supplied social-post material into evidence-labeled first-principles and business-methodology findings for Miles. Use when the user asks what an X creator actually did, what problem they answered, what causal principle or method is present, what Miles can transfer, or what claims should not be trusted; do not use for ordinary summarization, comment-section analysis, automatic X collection, storage, or publishing."
---

# Miles X Methodology

Analyze one real source package into a direct, evidence-bounded methodology
report. Do not turn a URL, popularity signal, or confident writing into proof.

## Confirm the input package

Accept any of these:

- supplied post text and its source URL;
- screenshots whose visible text can be read;
- structured post data containing author, text, media descriptions, quoted post,
  necessary parent context, and links;
- a URL whose real content has already been retrieved by the selected external
  acquisition executor.

If the request contains only a URL, do not infer its content. Return control to
the `mileswang` route so an applicable browser or research Skill from the
host-provided active Skill catalog can retrieve it. Keep the selected executor
unchanged. After acquisition, analyze only the material actually returned.

If the selected acquisition executor fails or leaves essential content missing,
name the missing item and stop or lower the conclusion. Do not rediscover or replace the selected executor from disk folders, plugin caches, installed inventories, or configuration files.

Comments are excluded by default. A quoted post, necessary parent, image, video,
or external document enters the evidence set only after its content was actually
read. Never treat a URL, filename, thumbnail, or paraphrase as the content.

## Build an evidence ledger

Before drawing conclusions, separate each material claim with exactly one of
these labels:

- `来源明确`: directly traceable to identified source material;
- `事实摘要`: a faithful summary of what the supplied material says or shows;
- `AI 推断`: a causal or methodological interpretation not stated by the author;
- `未核验主张`: a number, result, attribution, or general claim lacking current
  supporting evidence;
- `Miles 可迁移行动`: a proposed action for Miles, not a claim about the author.

Read [analysis contract](references/analysis-contract.md) before writing. Use
[report template](references/report-template.md) for the final shape. Read
[anonymous cases](references/anonymous-cases.md) only when an input is incomplete
or the difference between summary and methodology is unclear.

## Answer the protected questions

Answer all five without collapsing them into one slogan:

1. What did the creator say happened or was done?
2. What problem did the creator answer?
3. What underlying causal principle explains the result?
4. What repeatable method did the creator use or imply?
5. What can Miles transfer into creator content and business practice?

Then identify what cannot be trusted yet, the applicability boundary, and the
smallest comparison or action that could verify the transferable claim.

First-principles analysis must state a causal chain. If the creator did not say
it explicitly, label it `AI 推断`. Do not upgrade a repeated opinion into a
stable author methodology when no author history was supplied.

## Keep the report useful

- Lead with the actual finding, not praise or a generic summary.
- Preserve disagreements, hidden assumptions, costs, and stop conditions.
- Prefer one concrete transferable action over a list of inspirational ideas.
- Do not shorten the report by deleting evidence boundaries, counterclaims, or
  the minimum verification action.
- Do not add collection, storage, Feishu, publishing, or browser-extension work.

## Protect Miles personal information

Keep public Miles brand references, but do not include non-brand contact
details, private paths, account identifiers, chats, private source records, or
unpublished personal examples in the report or acquisition handoff. Replace
them with role-based placeholders or stop if the analysis depends on exposure.

## Respect the routing boundary

Use the host-provided active Skill catalog as the only availability authority
and keep the selected executor unchanged. Do not rediscover or replace the selected executor from disk folders, plugin caches, installed inventories, or configuration files. This Skill owns the analysis, not external content access.
