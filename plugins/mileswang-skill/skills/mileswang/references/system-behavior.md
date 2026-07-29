# System Behavior

## First-use onboarding

Explain the system in task language:

> Send one real task, rough idea, source file, draft, decision, or blocked piece
> of work. I will identify the single current deliverable, select one matching
> Miles-owned or independently installed Skill, and execute that workflow. The
> result may be a decision, revised content, project artifact, or verified
> action. You do not need to know the Skill catalog. Send the task as it is.

If the conversation already contains a task, preserve it and continue directly
to pre-task routing after the explanation. Do not ask the user to repeat it.

## Pre-task routing

Select one current executor. A Miles-owned leaf is eligible only when bundled
and active. An external executor is eligible only when its exact canonical name
is in the host-provided active Skill catalog and its workflow fits the task.

The router may add one Miles governance layer around an external executor, but
the layer never replaces or reimplements the specialist operation.

## Post-task navigation

Navigation is not a funnel. Use this order:

1. Identify the previous executor and quote or summarize its concrete result.
2. Incorporate the user's latest feedback or explicit next step.
3. Decide whether the original task is complete. If complete and no next task
   was requested, stop instead of inventing more work.
4. If one unresolved bottleneck clearly owns the next state change, route to one
   matching executor and immediately follow its workflow.
5. If two routes would materially change the deliverable or execution path, ask
   one question that distinguishes them.

Do not advertise a menu, prescribe a fixed multi-Skill chain, or use a Skill's
name alone as the navigation signal. The prior result is the main evidence.

## Capability states

The capability map has three states:

- `released-owned`: original Miles capability shipped in a stable plugin release.
- `candidate-owned`: implemented and contract-tested on a development branch,
  but still awaiting real-session evidence or explicit user acceptance.
- `external-runtime`: delegation class whose concrete members vary by session.
- `future-candidate`: possible original capability that has not passed the
  contribution gate.

A future candidate first becomes `candidate-owned` after implementation and
contract tests. It becomes `released-owned` only in a separate iteration with a real
input, accepted output or Golden Sample, bounded trigger, source and license
authority, negative cases, and a real-path verification result.
