# Atlas 2 — Analogy Discrimination Benchmark

**The existing atlas is frozen.** Everything under `snapshot/` and `claims/` is a
read-only pinned capture and must not be edited. Atlas 2 reads from it and writes
only inside `atlas2/`. Any change to the frozen atlas invalidates every
pre-registered number here.

Atlas 2 asks a narrower question than the atlas does: **can a blind reviewer,
using the rubric, separate an established correspondence from a vacuous one —
and where do the atlas's own records fall between them?**

## Why this is separate from the atlas

The atlas's schema accepts vacuous correspondences as easily as real ones (see
`../DATA_DEFECTS.md` §D6). Four obviously empty morphisms were constructed in
minutes and pass the same six fields. So the atlas is a set of *claims with no
ground truth*, and no amount of re-reading it will produce ground truth.

Atlas 2 supplies ground truth on both sides — established dictionaries as
positives, hand-built vacuous items as negatives — and then locates the atlas
records against that scale.

## Layout

| Path | Purpose |
|---|---|
| `schema/item.schema.json` | The blind item every reviewer sees |
| `schema/label.schema.json` | Private labels, joined by `item_id` |
| `tools/normalise_items.py` | Rewrite the 90 atlas records into uniform style, strip leaks |
| `tools/shuffle.py` | Generate hard negatives (constrained swaps) |
| `tools/leakage_check.py` | Must pass before any human scoring |
| `items/` | Generated. Regenerable; do not hand-edit |
| `PREREGISTRATION.md` | Decision rules fixed before scoring |

## Non-goals

- Proving any atlas record correct.
- Extending the atlas, or fixing it.
- Verifying citations.

## Scope

**90 records, not 3,331.** The workbench's 3,331 edges are problem→problem
structural links with no `math_invariant`, `physics_invariant` or
`transfer_operator` — the rubric cannot score them. Only
`atlas_morphism_records` carries the six fields, and that is 90.

## Reproduce

```bash
python3 atlas2/tools/normalise_items.py     # frozen snapshot -> blind items + labels
python3 atlas2/tools/shuffle.py             # hard negatives
python3 atlas2/tools/leakage_check.py       # gate: must pass before scoring
```
