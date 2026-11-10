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
| `KNOWN_ISSUES.md` | Defects in this substrate and its coverage, reproducible |
| `DATA_DEFECTS.md` | Concrete defects found in the atlas data, with record ids and fixes |
| `EVALUATION_LOG.md` | Fill this in with your findings |
| `curation/` | Changes made to production data, with backups and verification |
| `tools/` | The exporter and an integrity validator |

## What is out of scope

- The solvent index, its dimensions and weights, and any solvability scoring.
- The Prima Materia transfer-matrix framework.
- Any problem statement not anchored in `anchors/GROUND_TRUTH.md`.
- Live API behaviour. Anything that changes between runs is not evaluable.
- **`atlas_formalization_coverage`.** The atlas separately tracks upstream
  formal-conjectures progress (1,011 problems, 818 with solved declarations). That
  is a claim about Lean coverage, not about morphisms, and it is not captured in
  this snapshot. Do not read its absence as an omission in the atlas; evaluate it
  separately or not at all.

## Canonical numbers

Use these denominators and quote them. Corpus-level findings are meaningless
without one.

| Quantity | Value | Note |
|---|---|---|
| Claims in this snapshot | **90** | captured at a pinned commit |
| Records in the source table | **90** | all reachable — see `KNOWN_ISSUES.md` §1 |
| Problems carrying claims | **64** | |
| Claims with a citation reference | **42** (47%) | 13 curated + 29 parsed from prose |
| Claims with no citation reference | **48** (53%) | carry an experiment note only |
| Claims with no transfer operator | **5** (6%) | marked `incomplete`, hidden from default results |
| Physics objects in snapshot | **66** of 66 | full table via `/api/physics` |

The honest headline for any corpus-level statement is **90 served claims** over 64
problems. Not 92, and not 1011.


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

## License

Apache-2.0 for the tooling and documentation — see `LICENSE`. The snapshot data is
captured from the public ErdosAtlas API and is redistributed here for evaluation;
it is a dated copy, not a live feed, and the atlas remains the source of truth.

## Status

Prepared for external evaluation. The snapshot is pinned and `tools/validate.py`
verifies it. Nothing in this repository is peer reviewed; `KNOWN_ISSUES.md` and
`DATA_DEFECTS.md` state what is known to be wrong or missing.
