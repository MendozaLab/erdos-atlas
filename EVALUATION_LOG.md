# Evaluation log

Copy this file, fill it in, and return it. Do not edit the original.

## Run metadata

| Field | Value |
|---|---|
| Evaluator (agent / person) | |
| Date | |
| Snapshot commit / manifest `snapshot_utc` | |
| `tools/validate.py` result | |
| Claims evaluated | of 90 |
| Time spent | |

## Coverage caveat

State here whether your conclusions are affected by the remaining coverage gap
in `KNOWN_ISSUES.md`. Findings about *individual* claims are unaffected. Any
finding about the corpus as a whole must be labelled conditional.

## Per-claim findings

One block per claim. Quote the record field you are judging — a verdict without a
quoted field is not reviewable.

```
### CLAIM: E<math_id>-><physics_id>
Axis 1 (fidelity)   : /4 —
Axis 2 (efficacy)   : /4 —
Axis 3 (evidence)   : /4 —
Axis 4 (boundary)   : /4 —
Verdict             : HOLDS | PLAUSIBLE | DECORATIVE | BROKEN | UNEVALUABLE
Finding type        : defect | weakness | gap
Evidence            : <quote the field(s)>
Justification       : <one or two sentences>
Anchor check        : <what the original statement actually says, if it differs>
```

## Summary

**Survival.** `__` of `__` evaluated claims reached HOLDS. `__` PLAUSIBLE,
`__` DECORATIVE, `__` BROKEN, `__` UNEVALUABLE.

**Highest-value findings.** The two or three things a maintainer should fix
first, in order.

1.
2.
3.

**`proved` claims specifically.** Of the claims asserting `strength: proved`,
how many do you judge actually establish a cross-domain transfer rather than
crediting a classical result? Name them.

**Systematic patterns.** Anything that recurs across claims and looks like a
methodological habit rather than an isolated slip.

## Gaps

Claims you could not evaluate, and precisely what was missing. This section is a
deliverable, not an apology — it tells the maintainer what the substrate itself
needs.

| Claim | What was missing |
|---|---|
| | |

## Reviewer honesty

- Did you verify citations, or accept them? Say which.
- Did you read the original problem statements, or work from the atlas's
  paraphrase of them?
- Anything you were unsure about but did not record.
