# Worked Examples and Checklists

These examples illustrate behavior. They do not claim that any external project was inspected or completed.

## Example 1: “Deploy the latest version”

Concrete input:

> Deploy the latest customer-support dashboard today.

Read-only inspection in this example finds:

- `main` at commit `a1b2c3d`, with a recorded smoke test;
- a worktree at commit `d4e5f6a`, with uncommitted changes to the ticket flow;
- the public site reporting commit `98ab765`;
- no evidence that the worktree changes passed the real ticket-submission path.

Correct output before any deployment:

```markdown
Status: blocked

Core task: change the currently public dashboard into the user-confirmed authoritative version without losing the working ticket flow.

Authority candidates:
- main / a1b2c3d: smoke-tested, but older than the worktree changes.
- worktree / d4e5f6a + uncommitted changes: contains the newest feature, real flow unverified.
- public / 98ab765: currently running, source relationship not yet confirmed.

Highest-impact question: Which candidate should be authoritative: the tested main version or the newer unverified worktree?

No deployment has started.
```

Passing a local build would not resolve this version fork.

## Example 2: a parser fix with a proxy-metric trap

Concrete input:

> Fix the CSV importer. A file containing a blank line passes validation but imports zero contacts.

Bounded contract:

- Input state: the supplied anonymous CSV passes validation and creates zero contacts.
- Target state: the same file creates the two valid contacts and reports the skipped blank row.
- Scope: parser and its focused tests; exclude interface redesign and unrelated import formats.
- Primary hypothesis: an empty record terminates iteration instead of being skipped.
- Acceptance path: upload the same CSV through the running import entrypoint and inspect created contacts plus the row report.
- Rollback: restore the protected parser baseline if valid-row behavior regresses.

Evidence report after a correct run:

```markdown
Proven: the supplied CSV created two contacts through the running import entrypoint and reported one skipped blank row.
Proven: the protected valid-only sample still imports the same two contacts.
Partially proven: broader CSV dialect compatibility was not tested and is outside this iteration.
```

Unit tests alone would be only partial evidence because the reported failure occurs in the running import path.

## Pre-implementation checklist

- [ ] Confirm one state change and one iteration deliverable.
- [ ] Inspect the real inputs and existing project documents.
- [ ] Record all five contract answers in one authority document.
- [ ] Resolve every material implementation fork.
- [ ] Check the host-provided active Skill catalog and relevant reusable public implementations.
- [ ] Establish version authority for restore, migration, publication, deployment, replacement, rebuild, or deletion.
- [ ] Protect a comparison baseline and rollback.
- [ ] State one primary causal hypothesis.

## Completion checklist

- [ ] Use the intended input and the correct object.
- [ ] Exercise the real entrypoint and core operation.
- [ ] Inspect the actual produced result.
- [ ] Test failure behavior instead of accepting a success-shaped fallback.
- [ ] Check both correctness and usefulness.
- [ ] Compare against the baseline with the same input.
- [ ] Label evidence as proven, partially proven, inferred, or not verified.
- [ ] Report remaining limits without expanding the current scope.
