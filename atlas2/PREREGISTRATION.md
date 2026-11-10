# Pre-registration — Atlas 2 analogy discrimination benchmark

Committed **before** any item is scored by any reviewer. Fixed now, not tuned
later. Deviations must be recorded with their reason and reported alongside the
result, not silently applied.

The frozen atlas under `../snapshot/` is the input and is never modified.

## Scope

- **Unit:** the 90 records in `atlas_morphism_records`, deduplicated to **82**
  distinct items (8 are exact content duplicates).
- **Excluded:** the 5 `record_status='incomplete'` records.
- **Not the workbench.** Its 3,331 edges are problem→problem links carrying no
  invariants or transfer operator; the rubric cannot score them.

## Classes

| Class | Definition | n (target) |
|---|---|---|
| `gold` | Established dictionary from the literature **with a named crossing result** | 15–20 |
| `established_non_transferring` | Real dictionary, no crossing result | 10–15 |
| `trivial_exact` | A true identity carrying no result | 10 |
| `decoy` | Hand-built vacuous correspondence | 30 |
| `shuffled` | Constraint-swapped pair, four variants | ~155 (generated) |
| `atlas` | The 82 frozen items | 82 |

**The `established_non_transferring` class is mandatory.** A dictionary that
supplies no crossing result is not a positive under a rubric whose Axis 2 requires
naming one. Conflating the two is the error most likely to make this benchmark
report "the rubric cannot discriminate" when the fault is class definition.

Promotion rule, applied before scoring: a `gold` item must cite a specific theorem,
bound or construction that crosses. If the author cannot name one, the item is
reclassified `established_non_transferring` — never dropped, because that class is
a result in itself.

## Leakage gate — must pass before any scoring

Measured on the frozen atlas class alone, 2026-11-10:

| Target | content AUC | style AUC | **length-only AUC** | perm p |
|---|---|---|---|---|
| authoring session (n=46, binary) | 1.000 | 1.000 | **1.000** | 0.005 |
| physics category (n=48, 5-way) | 0.930 | 0.859 | **0.784** | 0.005 |

Two authoring sessions are separated *perfectly* by field lengths alone
(52.0 ± 4.4 vs 48.0 ± 6.2 words). Physics category is predictable from lengths at
0.784. This corpus is fingerprinted by brevity.

**Gate rules, binding:**

1. Length control happens at **authoring time, not afterwards**. Every gold, decoy
   and trivial-exact item is written to the length profile of the frozen atlas
   (per-field word counts inside its interquartile range). Authors are given the
   profile; items outside it are returned, not normalised.
2. Truncation is **not** a substitute. Sweeping the cap and re-scoring author
   separation from lengths alone: cap 40 → AUC 0.996, cap 12 → 0.994, cap 8 (78% of
   text retained) → 0.994, cap 5 (54% retained) → 1.000. The fingerprint is the
   per-field length *profile*, which survives truncation because it is a shape, not
   a total. See `tools/equalise_lengths.py`, retained only so the negative result
   reproduces.
3. The gate runs on the **`class` label** once items exist, and must show
   style-only and length-only AUC **< 0.65**. Above that the split leaks and no
   scoring result is admissible.
4. The gate report is committed with the items. A run without it is void.
5. The author-length leak measured on the atlas class alone cannot be fixed post
   hoc and does not by itself invalidate the benchmark, because every atlas item
   shares one class. It matters only if authorship correlates with class, which
   rule 1 exists to prevent.

## Scoring protocol

1. Items presented in random order, blind to class. Labels live outside the
   public tree; the private split carries a canary string.
2. Reviewers score Axis 1, Axis 2, Axis 4 and assign a verdict. Axis 3 is dropped
   because citations are stripped.
3. Axis 2 above 2 requires naming the result that crosses.
4. **Three conditions**, because two conflate judgement with compliance:
   - **A: fields only**
   - **B: fields + rubric**
   - **C: fields + rubric with the "name the resulting crossing" requirement removed**
   The B−A gap measures what the rubric adds. The C−B gap measures how much of
   that is the instruction rather than the criteria. If C ≈ A and B ≫ A, the
   rubric is not adding judgement, it is adding a forced answer.
5. At least three domain experts and three model families, each run twice.

## Metrics and decision rules

Primary metric: AUROC of gold vs (decoy ∪ shuffled) on the Axis 2 score.

| Metric | Pass | Fail | Note |
|---|---|---|---|
| AUROC, gold vs (decoy ∪ shuffled), Axis 2 | **CI lower bound >= 0.75** | CI upper bound <= 0.65 | Judged on the 95% CI lower bound, **not** the point estimate: with 15-20 gold items the CI is about +/-0.10 and a point threshold can pass on luck |
| Decoys scored PLAUSIBLE or HOLDS | <= 10% | > 30% | The core specificity test |
| `established_non_transferring` vs `gold` separation | reported | reported | No threshold. If these two do not separate, the crossing-result criterion is not being applied and the gold class is not doing its job |
| Krippendorff's alpha, ordinal axes | >= 0.60 | < 0.40 | Three or more raters |
| Atlas items above 95th percentile of shuffled | reported | none | The honest headline for the atlas. Uses constrained variants, not unconstrained random |
| Style/length leakage AUC on class | < 0.65 | >= 0.65 | Gate. Blocks scoring entirely |

Thresholds are fixed as written. A fail is a publishable result about the rubric.

## Stopping rules

- If the leakage gate fails after equalisation, stop. Report the leakage instead
  of a discrimination number.
- If fewer than 12 gold items survive the crossing-result promotion, the primary
  metric is reported as underpowered rather than as pass or fail.
- If Krippendorff's alpha is below 0.40, report the disagreement structure; do not
  average the raters away.

## Known negatives already in hand

The frozen atlas contains one `refuted-locally` record. That is a ground-truth
negative established by the project itself and it belongs in the `decoy` class with
the refutation cited. The two `proved` records are candidate positives, admissible
only if a crossing result is named.

## Threats to validity

- **Memorisation.** Famous dictionaries will be recognised. Gold items must be
  obscure-but-established by default; famous ones are analysed as a separate
  stratum and reported both ways.
- **Author bias.** Decoys written by the project team will be too easy or too hard.
  Outsiders write both gold and decoys; the leakage gate is the check on whether
  authorship is detectable.
- **Small samples.** Intervals, not point estimates. 15-20 gold items will not
  support a thresholded claim on their own.
- **The rubric may be too strict to admit real dictionaries.** That is the
  hypothesis this benchmark exists to test, and it is why
  `established_non_transferring` is a separate class rather than a gold subclass.

## What would falsify the benchmark itself

If `gold` and `established_non_transferring` do not separate on Axis 2, then the
crossing-result criterion is not measurable by reviewers and the primary metric is
meaningless. That outcome is reported as a failure of the instrument.

Pre-registered 2026-11-10, before any scoring.
