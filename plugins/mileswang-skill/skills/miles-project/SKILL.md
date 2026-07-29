---
name: miles-project
description: "Scope and execute evidence-backed project work from a real input state to a verifiable target state. Use for building, changing, repairing, restoring, migrating, publishing, or deploying products, codebases, automations, and workflows; do not use for a simple answer or a content-only revision."
---

# Miles Project

Turn a project request into one bounded state change, then implement and verify that state change through its real use path.

## Establish the project contract

Inspect the relevant files, repositories, running entrypoints, and existing project documents before writing. For non-trivial product work, keep the following five answers in one authoritative Markdown requirement document. Prefer an existing `PROJECT.md` instead of creating competing sources of truth.

1. **Core task:** Define the confirmed input state and the target state in one sentence.
2. **Deliverable and user:** Name the artifact, its user, and the real usage scenario for this iteration.
3. **Authoritative inputs:** List the exact source files, data, versions, or original materials that govern the work.
4. **Scope and constraints:** State what this iteration includes, excludes, and must not violate.
5. **Acceptance evidence:** Name the real operation and observable result that will prove success, plus the stop condition.

Use the [project contract template](references/project-contract.md) when no equivalent document exists.

## Check the implementation fork

Ask whether any unresolved item has two or more reasonable answers that would change the product shape, target user, data source, platform, core flow, main technical path, safety boundary, or rework cost.

- If a material fork remains, mark the contract `blocked`, ask only the highest-impact question, and stop before implementation, dependency installation, broad research, or bulk generation.
- If the five answers are unique and executable, mark the contract `ready-to-build`, stop asking exploratory questions, and begin the fixed loop: implement, verify, deliver.
- Assume only cheap, reversible details such as wording or filenames. Record the assumption.

## Reuse before creating

Use the host-provided active Skill catalog as the only availability authority before implementing a general capability. When network access and project scope permit, inspect mature, relevant public implementations before building a new one. Treat stars and popularity as discovery signals only. Verify license compatibility, maintenance state, security, actual input/output behavior, and fit before adopting code or workflows.

## Respect the router boundary

When `mileswang` invokes this Skill, keep the selected executor unchanged. Do not rediscover or replace the selected executor from disk folders, plugin caches, local inventories, or configuration files.

## Establish version authority

Apply this gate before any task involving “latest,” restore, replacement, migration, rebuild, publication, deployment, or deletion.

1. Enumerate every plausible source within scope: related directories, branches, tags, commits, worktrees, uncommitted changes, backups, historical outputs, the running version, and any user-designated source.
2. Compare project identity, repository state, commit, uncommitted changes, core behavior, known acceptance results, and the version behind the real entrypoint.
3. Choose authority in this order: user-confirmed source, verified stable baseline, workspace with the latest validated change, then repository history and functional differences. Use modification time only as supporting evidence.
4. If two plausible candidates remain, stop the destructive or publishing action and show their concrete differences.
5. Before acting, report the authoritative source, operation target, selection basis, and rollback location.

Do not call a path, branch name, passing build, or open page “the latest version” without this evidence.

## Preserve a baseline and test one cause

- Protect any user-confirmed working version with its code, configuration, input conditions, output shape, anonymous sample, and acceptance result.
- Tie each change to one primary causal hypothesis. State the expected result, comparison baseline, and rollback before changing it.
- Compare before and after with the same input.
- Do not change the model, prompt, architecture, data, interface, and validation rules simultaneously.
- After two unsuccessful changes to the same problem, stop patching. Recheck the problem definition, input, data flow, causal hypothesis, and system boundary.
- Reject complexity that does not directly improve the core target.

## Verify correctness and usefulness

Run both gates:

1. **Correctness gate:** Verify the input and object, core processing, data and structure, safety, failure handling, and operational reliability.
2. **Usefulness gate:** Verify that the result is concrete, understandable, usable in the stated scenario, and actually completes the user's task.

Then exercise the real path: supply the intended input through the real entrypoint, confirm that the core operation actually ran, inspect the produced result, and verify that failure was not disguised as success. Build success, tests, HTTP status, page visibility, and field presence are intermediate evidence unless they are the acceptance target.

Classify every completion claim:

- **Proven:** observed in the current run through the required path;
- **Partially proven:** an intermediate gate passed but the final path did not;
- **Inferred:** supported by evidence but not directly observed;
- **Not verified:** no current evidence.

Read [worked examples and checklists](references/examples.md) when the request is vague, version-sensitive, or easy to “complete” with a proxy metric.

## Deliver against the original goal

Lead with the actual outcome. Report changed artifacts, real verification evidence, unresolved limits, and rollback. Do not claim more than the evidence level supports. Record future ideas separately; do not add them to the active iteration.

## Protect Miles personal information

Allow the public Miles brand, but keep non-brand contact details, private paths,
account identifiers, credentials, chats, and local source evidence out of
public artifacts, logs, errors, and Agent handoffs. Use anonymous fixtures and
role-based placeholders; stop a publication or delegation that would expose the
protected value.
