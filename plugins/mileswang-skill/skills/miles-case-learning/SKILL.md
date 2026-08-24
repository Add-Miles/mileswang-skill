---
name: miles-case-learning
description: "Guide evidence-based learning from a supplied product, tool, workflow, repository, creator post, or public case. Use when the user wants to understand how a real example works, distinguish evidence from inference, trace inputs, rules, outputs, validation, and failure handling, then design one safe minimal reproduction. Do not use to immediately build a complete product, write a PRD, publish content, or collect private data."
---

# Miles Case Learning

Turn an unfamiliar real-world case into **verifiable understanding**, not an
immediate clone. The goal is for the user to see how the example works, what is
actually evidenced, what the smallest reproducible portion is, and where the
flow can fail.

Use the user's language in the final learning card. Do not turn this workflow
into a product-requirements interview or force the user to make unnecessary
product decisions before learning can begin.

## Confirm the learning material

Accept a supplied product URL, screenshots, screen recording, public repository,
README, official documentation, author or founder post, changelog, issue,
public case study, or a concrete observed workflow.

If material is missing, identify the smallest missing evidence. Prefer sources
in this order:

1. official product documentation, public API documentation, public repository
   README, source, examples, and architecture notes;
2. an author's or founder's public explanation, release note, or demonstration;
3. public issues, changelogs, user feedback, and documented failures;
4. third-party tutorials only as secondary context.

A URL, filename, screenshot thumbnail, popularity signal, or confident claim is
not evidence by itself. If the user supplies only a URL, return control to the
`mileswang` route so an applicable active acquisition Skill can retrieve the
real material. Analyze only material that has actually been returned.

## Protect Miles personal information

Never request private credentials, real customer data, unpublished source code,
or private chats in order to make the case understandable. Keep public brand
references but do not include non-brand personal information, account
identifiers, private paths, tokens, or chat content in any output or Agent handoff.

## Separate observation, evidence, and inference

Before proposing an implementation or conclusion, create a short evidence
ledger. Label every important statement as exactly one of:

- **Observed fact**: directly visible in supplied material;
- **Documented fact**: supported by an identified public primary source;
- **Inference**: a plausible mechanism that is not yet confirmed;
- **Unknown**: a necessary detail that the material does not establish;
- **Learning action**: a proposed test for the user, not a claim about the
  original author or product.

Do not upgrade a black-box guess into the original implementation. If a
mechanism cannot be verified, retain the uncertainty and design a small test
instead of inventing an explanation.

## Follow the case-to-method workflow

### 1. Observe before inventing

Describe only what can be seen or evidenced:

| Item | Question |
| --- | --- |
| User action | What does a user or external system do first? |
| Input | What information or event enters the flow? |
| Output | What result becomes visible? |
| Validation | How can success or failure be observed? |
| Hidden rule | What rule must exist for that result to occur? |
| Likely failure | Where might the flow break or become unreliable? |

Mark hidden rules and likely failures as **Inference** until evidence confirms
them.

### 2. Return to evidence

Investigate only the sources needed to confirm the current chain. For example,
use documentation to check permissions, inputs, outputs, and limits; a README
and examples to identify the minimum path; issues and changelogs to find real
failure modes; and an author's public explanation to understand the intended
use case.

Do not begin by reading an entire codebase. Start with the README, architecture
notes, examples, relevant entry point, and the issue or documentation section
that bears on the current unknown.

### 3. Draw the shortest chain

Reduce the case to this explicit form:

```text
Input → processing/rule → output → validation → failure handling
```

Use only documented facts and clearly labeled inferences. If AI is involved,
state what it receives, what it returns, who verifies it, and what happens when
it is wrong. “It uses AI” is not a processing step.

### 4. Reproduce only one small segment

Choose a segment that can normally be tested in 30–60 minutes, has a specific
input and observable output, exposes one real rule or failure mode, and can run
with sample or simulated data.

Do not start by copying the whole product or connecting production accounts,
payment, sensitive data, or public publishing channels. If a real external
operation becomes necessary, stop at a simulation or request explicit user
confirmation before taking that operation.

### 5. Turn a blockage into a reusable rule

For every result that differs from expectation, record:

```text
Expected result → actual result → layer → evidence used to locate it → how to verify the fix
```

The layer may be a rule, data, interface, permission, UI, code, or unknown.
Only recommend a template, script, or new Skill after the same action has shown
stable value across more than one relevant case.

## Deliver a case learning card

Use [the case learning card](templates/case-learning-card.md). Every result
must include:

- evidence with its source or material location;
- clearly separated inferences and unknowns;
- the shortest input-to-failure chain;
- one bounded, safe minimal reproduction; and
- one concise transferable rule.

If the user wants explanation only, provide the learning card in plain language
without requiring reproduction. If the input cannot support a defensible chain,
name the missing evidence and stop there rather than filling gaps with a
fictional implementation.

## Respect the routing boundary

Use the host-provided active Skill catalog as the only availability authority.
When a separate executor must acquire source material, keep the selected executor unchanged.
Do not rediscover or replace the selected executor from disk folders,
plugin caches, installed inventories, or configuration files.

## Respect adjacent Skill boundaries

- Use `miles-x-methodology` when the primary deliverable is evidence-bounded
  methodology analysis of supplied X/social-post material.
- Use `miles-project` when the user wants to build, modify, publish, deploy, or
  otherwise execute a real project.
- Use `miles-prd-framework` when the user needs a PRD writing structure.
- This Skill does not collect accounts, automate publishing, store a case
  database, or create a full product from the case.
