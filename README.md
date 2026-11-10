# ErdosAtlas — external evaluation substrate

This repository exists for one purpose: to let an **independent agent or reviewer
evaluate the ErdosAtlas** claims against a fixed, reproducible target, without
access to the private research monorepo.

It is not the atlas. It is the surface you evaluate the atlas through.

## What the atlas claims

ErdosAtlas proposes *putative morphisms* between Erdős problems and physical
systems: a structural correspondence, a transfer operator that carries a
mathematical invariant to a physical one, and a declared point at which the
correspondence breaks. Each morphism is a falsifiable hypothesis, not a detected
fact.

The atlas also ranks problems by a *solvent index* estimating structural
attackability. **That scoring machinery is out of scope here** and is not
included. Evaluating a proprietary ranking algorithm is neither possible from
this repo nor the point. What you can evaluate is the morphism content and the
claim discipline around it.

## What is in scope

| Path | What it holds |
|---|---|
| `snapshot/` | A dated, immutable capture of the public API. Evaluate this, not the live API. |
| `snapshot/manifest.json` | Provenance: capture time, method, counts, SHA-256 of every payload, known gaps |
| `claims/CLAIMS_REGISTER.json` | Every morphism restated as a claim with an explicit falsification condition |
| `claims/CLAIMS_REGISTER.md` | Human-readable view of the same |
| `anchors/GROUND_TRUTH.md` | Where to check each claim against the outside world |
| `rubric/MORPHISM_RUBRIC.md` | The judging criteria, so findings are comparable between evaluators |
| `EVALUATION_BRIEF.md` | The task: what to do, in what order, what to return |
| `EVALUATION_LOG.md` | Fill this in with your findings |
| `tools/` | The exporter and an integrity validator |

## What is out of scope

- The solvent index, its dimensions and weights, and any solvability scoring.
- The Prima Materia transfer-matrix framework.
- Any problem statement not anchored in `anchors/GROUND_TRUTH.md`.
- Live API behaviour. Anything that changes between runs is not evaluable.

## The one rule that matters

Evaluate the **snapshot**, not the API. The API is liquid; findings against it
cannot be reproduced or compared across evaluations. `snapshot/manifest.json`
pins what you should be looking at, and `tools/validate.py` confirms your copy
is intact before you start.

## Honest state of this substrate

Written by the same organisation that produced the atlas, which makes it a
contested document. What follows is what is genuinely weak, so you can discount
accordingly:

- **Coverage is partial.** The API exposes no full problem catalogue, only the
  top 100 by solvent index. Morphisms are discoverable only by probing problem
  ids. The manifest records exactly how many were captured against how many the
  API declares, and states the gap. Do not read the snapshot as the whole atlas.
- **Claims were derived mechanically.** `CLAIMS_REGISTER.json` was generated
  from the morphism records' own fields. The falsification conditions are
  restatements, not independent analysis. Where a record was ambiguous, the
  ambiguity is preserved rather than resolved — if a claim looks vague, that is
  a finding, and it is not smoothed over here.
- **Ground truth is thin.** For most problems the only external anchor is the
  erdosproblems.com statement and the literature the record itself cites. Where
  a citation could not be verified at capture time, it is marked unverified
  rather than presented as checked.
- **No maintainer review.** Nothing here has been peer reviewed. Absence of
  criticism so far means only that the work is recent.

## Reporting

Use `EVALUATION_LOG.md`. Separate three kinds of finding clearly, because they
carry very different weight:

1. **Defects** — a claim is wrong, incoherent, or contradicted by its own cited
   source.
2. **Weaknesses** — a claim is defensible but the evidence does not support the
   confidence asserted (`strength` says more than the citation earns).
3. **Gaps** — you could not evaluate it because the substrate or the anchor was
   insufficient.

A finding of type 3 is not a failure of your review and should be reported
plainly; it is one of the things this exercise is designed to surface.
