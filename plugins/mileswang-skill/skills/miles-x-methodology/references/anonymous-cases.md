# Anonymous Cases

These synthetic cases demonstrate boundaries, not expected wording.

## Adequate input

Input: a creator describes replacing a weekly manual report with a script,
provides the old time cost, shows the same report after automation, and notes two
weeks of use.

Good behavior:

- summarize the actual before and after as `事实摘要`;
- label the claim that automation caused all saved time as `AI 推断` unless the
  comparison controls for changed report scope;
- extract a repeatable method with a stop condition;
- propose testing one recurring Miles task with the same output requirement.

Bad behavior: “AI automation is the future” or a list of unrelated automation
ideas.

## URL only

Input: only a social-post URL.

Good behavior: use the already selected active acquisition executor, then
analyze returned content. If acquisition fails, report the missing post content
and stop.

Bad behavior: infer the post from its author, URL, engagement count, or memory.

## Missing media

Input: text says “the chart below proves the result,” but the chart was not
provided.

Good behavior: mark the result claim `未核验主张`, say the image is unread, and
avoid analyzing the claimed measurement.

## No author history

Input: one complete post with no earlier material.

Good behavior: analyze this post's method while stating that a stable long-term
author methodology cannot be determined.

## Comment request

Input: the post plus “also analyze all replies.”

Good behavior: state that comments are outside the default boundary and ask for
explicit confirmation of the expanded evidence set before using them.

## Rejected compression pattern

Bad behavior: replace the source, counterclaims, assumptions, boundaries, and
verification action with one catchy conclusion followed by five short answers.
Conciseness is useful only after the causal and evidence structure survives.
