# Morphism rubric

Score each claim on four axes, then assign a verdict. The axes are deliberately
independent: a morphism can be mathematically sound and still be decorative, and
that combination is worth naming.

## Axis 1 — Correspondence fidelity

Is the claimed invariant correspondence *the same object* on both sides, or a
family resemblance?

- **4 — Isomorphic.** The two invariants are provably the same structure, and you
  could state the translation without loss.
- **3 — Faithful.** A precise, checkable dictionary exists between them, even if
  not literally isomorphic.
- **2 — Partial.** The correspondence holds in a restricted regime, and the
  record's own `breakdown_boundary` honestly marks where it stops.
- **1 — Gestural.** The two sides are described by similar words; no explicit
  translation is supplied or implied.
- **0 — False.** The invariants are demonstrably not the same, or the
  correspondence contradicts a cited source.

## Axis 2 — Transfer efficacy

Does the transfer operator *do work*, or is it a label?

- **4 — Load-bearing.** The operator carries an actual result: a bound, a
  construction, or a proof technique crosses the boundary and yields something
  new or sharper.
- **3 — Useful.** It organises known facts on both sides into a shared frame and
  predicts at least one checkable statement.
- **2 — Suggestive.** It names an analogy that could plausibly be exploited, with
  no exploitation demonstrated.
- **1 — Decorative.** Replace it with "these things are both about X" and nothing
  is lost.
- **0 — Vacuous.** The operator is undefined, or does not act on the object it
  claims to act on.

Ask concretely: *if the physics column were deleted, would any mathematical
statement become harder to prove or any bound tighter?* No is 1 or 0.

## Axis 3 — Evidence honesty

Does the asserted confidence match what the citations earn?

- **4 — Earned.** `strength` is exactly as strong as the cited work supports, and
  the citations are *about* this correspondence.
- **3 — Sound.** Confidence is defensible; citations are adjacent but genuinely
  relevant.
- **2 — Optimistic.** The citations support a weaker claim than `strength`
  asserts.
- **1 — Inflated.** Citations are real but concern something else; `strength`
  borrows their authority.
- **0 — Unsupported.** No citation bears on the claim.

Classical theorems are the trap here. Sidon 1938 and Singer 1938 are true
regardless; whether they *establish a morphism* is a different question, and a
`proved` label that means "the underlying theorem is classical" is a category
error worth flagging.

## Axis 4 — Boundary integrity

Is `breakdown_boundary` where the correspondence actually fails?

- **4 — Precise and honest.** Names the real failure point, and the failure is
  genuine.
- **3 — Correct but loose.** The stated limit is real, if not the sharpest
  possible.
- **2 — Vague.** Gestures at a limit without specifying it.
- **1 — Self-serving.** Draws the boundary narrowly so the correspondence looks
  safe within it, when the analogy degrades earlier.
- **0 — Absent or false.** No boundary, or one contradicted by the record's own
  content.

## Verdicts

Map the four axes to one verdict. Do not average — use judgement, and say which
axis drove the verdict.

| Verdict | Meaning |
|---|---|
| **HOLDS** | Sound correspondence with real transfer. Safe to build on. |
| **PLAUSIBLE** | Genuine but under-exploited. Worth pursuing, not yet evidence. |
| **DECORATIVE** | Resemblance without transfer. Harmless, but must not be counted as evidence. |
| **BROKEN** | A specific, statable defect: wrong invariant, undefined operator, false boundary. |
| **UNEVALUABLE** | Substrate or anchor insufficient. Record the gap that blocked you. |

## Calibration requirements

- Quote the record field you are judging. A verdict without a quoted field is not
  reviewable.
- Distinguish *the cited theorem is true* from *the morphism is established*.
  These are the two most-confused statements in this corpus.
- If you rate above 2 on Axis 2 (transfer efficacy), name the result that
  crosses. If you cannot name one, the score is 2 or lower.
- UNEVALUABLE is a legitimate and useful verdict. Do not convert a gap into a
  weakness just to have a verdict — the distinction is the point.
