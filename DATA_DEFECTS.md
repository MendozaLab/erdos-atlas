# Data defects found while building this substrate

Concrete, reproducible defects in the atlas data as served. Each was checked
against a live API call, not inferred. Reported so they can be fixed rather than
silently evaluated.

## D1 — FIXED 2026-11-10 — Two placeholder records were in production

Resolved: both rows deleted from D1 and confirmed gone through the API.
See `curation/CURATION_LOG.md`. Retained below as the record of the defect.

```
MOR-114-PHYS-PT-001-1775139177870
MOR-114-PHYS-PT-001-1775139177883
```

Both carry `evidence: "test morphism"`, `math_object: null`, no
`math_invariant`, no `physics_invariant`, no `transfer_operator`. They are
test data that reached the serving layer and appear alongside real claims.

This also accounts for half the coverage puzzle: `114 -> PHYS-PT-001` appears
three times, and two of the three are these placeholders.

**Fix:** delete them, and add a constraint or filter so placeholder rows cannot
be served.

## D2 — `evidence` conflates two different things

The column is TEXT in all 37 records, but its contents are not the same kind of
thing:

| Kind | Count | Example |
|---|---|---|
| `citation_list` — a JSON array serialised into a string | 12 | `["Singer 1938","Sidon 1932",…]` |
| `experiment_note` — free text, not a citation | 23 | `L4-06 collider experiment, 5/5 tests PASS` |
| `test_placeholder` | 2 | `test morphism` |

Two problems in one. First, a structured array is being stored as a stringified
JSON blob, so consumers must guess whether to parse it. Second, and worse, **only
12 of 37 records (32%) carry any citation at all.** The remaining 23 carry a
note about an internal experiment.

That matters for evaluation: a reviewer checking "does the evidence support
`strength: proved`?" will find citations on 12 records and internal assertions on
23. Those are not the same epistemic object and should not share a field.

**Fix:** split into `citations` (structured array) and `evidence_note` (text),
and store citations as real JSON, not a serialised string.

## D3 — FIXED 2026-11-10 — Seven records had no transfer operator and no breakdown boundary

Resolved for the five real records: a `record_status` column was added and those
five are marked `incomplete`; the two placeholders were deleted under D1. The API
does not yet surface the mark, so they are still served as active until a worker
change lands. See `curation/CURATION_LOG.md`.

```
MOR-96-PHYS-C-004-1776365646328     (no transfer_operator, no breakdown_boundary)
MOR-97-PHYS-CL-003-1776365647253    (same)
MOR-389-PHYS-R-002-1776364597284    (same)
MOR-396-PHYS-R-002-1776364596453    (same)
MOR-505-PHYS-F-001-1776365642682    (same)
+ the two placeholders from D1
```

That is 19% of the corpus. By the atlas's own definition a morphism consists of a
correspondence *plus* a transfer operator *plus* a stated limit. These five have
neither mechanism nor limit — they assert a resemblance and stop.

They are not unevaluable by accident; they are incomplete as records. An
evaluator scoring them on the transfer-efficacy axis has nothing to score.

**Fix:** either supply the missing operator and boundary, or mark them
`incomplete` so they are excluded from corpus-level claims.

## D4 — A locally refuted morphism is still exposed as live

```
166 -> PHYS-KVN-001, strength: "refuted-locally"
```

The atlas tested this and refuted it, which is good practice and worth keeping as
a record. But `refuted-locally` is a fourth value in a `strength` field whose
other values describe current confidence, and it is served without any filter.

**Fix:** keep the record, exclude it from default queries, and surface it under
explicit opt-in. A refuted morphism appearing beside live ones invites a reader to
count it as a live claim.

## D5 — `strength: proved` on a classical citation (judgement, not error)

`mr-001` (30 → PHYS-SIG-001) is marked `proved` with citations Singer 1938,
Sidon 1932, Wichmann 1963, Erdős–Turán 1941. Those establish the classical
facts on each side. Whether they establish the *correspondence* is a separate
question, and the record does not say which reading `proved` means.

Flagged as an ambiguity to resolve, not a defect to fix. The evaluation rubric's
evidence axis exists for this.

## Credit where due

`mr-005` (89 → PHYS-SP-001) is the strongest record in the set and shows the
corpus can do this properly:

```
transfer_operator: L=D-A IS the tight-binding Hamiltonian: lambda_2(L) in graph
theory exactly equals E_1-E_0 in quantum mechanics on the same graph
```

That is a true statement of identity, not an analogy, and it is checkable. The
gap between this record and the five in D3 is the real quality spread in the
corpus.

## Priority

1. ~~**D1** — delete placeholder rows.~~ Done 2026-11-10.
2. ~~**D3** — mark or complete the five incomplete records.~~ Marked 2026-11-10;
   still needs the worker to expose `record_status`.
3. **D2** — split the evidence field. Mechanical, and it makes the 32%-cited
   figure visible instead of hidden.
4. **D4** — filter refuted records out of default queries.
5. **D5** — resolve what `proved` means. A definitional decision, not code.
