# Portable skeletons and contracts (open on demand)

## Minimal portable spine

```text
Meta → Problem → Goals / non-goals → Success criteria
→ Demand-type center (pick one)
→ Module contracts (each: duty, I/O, handoff, exception, acceptance)
→ Module interface table
→ Dependencies, exceptions, fallback
→ Acceptance, release, observability
→ Appendix / evidence
```

## Empty skeleton (topic-free)

Use role/structure slots only:

1. Document positioning — demand type, readers, one-line goal  
2. Background and problem — trigger evidence, current failure, who is hurt  
3. Goals, non-goals, scope — success, in/out, assumptions  
4. Actors and end-to-end flow — roles, order, priority  
5. Demand-type center — feature / experiment / risk / tools / platform / config  
6. Module contracts — repeat input, process, output, handoff, exception, acceptance  
7. Module interface table — upstream, output, downstream, use, condition  
8. Dependencies, exception paths, fallbacks  
9. Acceptance, release, observability — unit, interface, e2e, exception tests  
10. Appendix and evidence — standards, samples, diagrams, screenshots, terms  

## Type centers (titles only)

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

## Module contract checklist

For each module, all eight fields required: duty, upstream input, process, output, handoff, downstream use, exception, acceptance evidence.

## Interface table checklist

Every important transfer needs: upstream, output field/result, downstream, how used, when valid/stop.

## Mode B order

type/goals → scope → module contracts → interface table → acceptance/metrics → deps/risks → rest

## Gap rules

- Structure gap: blocks review or decision.
- Evidence gap: missing visual/attachment/sample; keep source template habits.
- Do not invent module merge because names look similar.

## Not a generate-PRD skill

Public “write PRD for coding agents” skills differ. This leaf extracts portable frames and contracts from complete docs, then fills half-draft structure only.
