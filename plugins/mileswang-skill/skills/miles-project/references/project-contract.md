# Project Contract Template

Use one contract for stable scope and acceptance. Keep changing run state in an existing status file when the project already has one.

```markdown
# Project Contract

Status: blocked | ready-to-build
Owner:
Confirmed:

## 1. Core task

Change [confirmed input state] into [verifiable target state].

## 2. Deliverable and user

- Deliverable:
- User:
- Usage scenario:

## 3. Authoritative inputs

- Source file, data, version, or original material:
- What has been verified:
- What remains an assumption:

## 4. Scope and constraints

### Included

-

### Excluded

-

### Must not violate

-

## 5. Acceptance evidence

- Real operation:
- Observable result:
- Failure condition:
- Stop condition:

## Implementation fork check

- Material unresolved fork:
- Highest-impact question, if blocked:
- Decision: blocked | ready-to-build

## Baseline and rollback

- Protected baseline:
- Comparison input:
- Rollback location or action:
```

## Contract quality check

- Express the core task as a state change, not a tool choice.
- Name one iteration deliverable instead of a future platform vision.
- Point to real inputs rather than remembered descriptions.
- Make exclusions explicit enough to prevent feature drift.
- Require evidence from the usage path, not merely from installation or construction.
- Mark the contract blocked when a material fork remains.
- Keep only one authoritative scope document.
