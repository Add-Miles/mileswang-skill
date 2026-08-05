# Demand-type skeletons (open on demand)

## Minimal spine

```text
Meta → Problem → Goals / non-goals → Success criteria
→ Users-scenes OR rules-states (one is the center)
→ Solution & scope → Main path / config → Dependencies → Metrics → Risks
→ Appendix
```

## Type titles only

### Feature / UX
Problem → Goals/non-goals → Scenarios → Main path → Rules → Edge cases → Acceptance → Tracking → Risk

### Growth / experiment
Hypothesis → Audience → Experiment design → Core/guard metrics → Variants → Window & decision → Rollout

### Transaction / risk
Problem → State machine → Rule table → Permissions/audit → Reconciliation → Compliance → Canary/rollback → Monitors

### Internal tools
Roles → Task flow → Fields → States & actions → Efficiency/error metrics → Config dependencies

### Platform capability
Caller scenarios → Capability bounds → API/event contract → Quotas/errors → Versioning → Examples → SLA

### Ops config
Goal → Config model → Scope → Priority/conflicts → Preview/approval → Rollback → Audit

## Half-draft check

For each framework section ask only:

1. Present?
2. Deep enough for a decision?
3. Blocking for review if missing?

Recommended fill order: type/goals → scope → main path or rule table → acceptance/metrics → deps/risks → rest.

## Not a generate-PRD skill

Most public PRD skills generate coding-agent specs from ideas.
This leaf extracts writing frames from complete docs and fills structure of half drafts only.
