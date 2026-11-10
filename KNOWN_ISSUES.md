# Known issues in this substrate

Read this before drawing conclusions. These are defects in the capture or in the
upstream API, not in your evaluation. Each one is reproducible.

## 1. The API exposes 40% of its own declared morphisms

`/api/health` declares `morphisms: 92`. The snapshot captured **37**.

How it was measured: `/api/morphisms/<id>` was queried for every id in
`1..6000`. Twenty-three problem ids returned records, totalling 37. Spot checks at
ids 6001, 7000, 9000 and 12000 returned zero, so the sweep range is not the
binding constraint.

Two hypotheses remain open:

1. About 55 records reference `math_problem_id` values that are not addressable
   through the `/api/morphisms/:id` route or are absent from the `problems`
   table.
2. `/api/health` counts rows that include soft-deleted or superseded records.

It could not be resolved at capture time. The authoritative table is
`atlas_morphism_records` in D1 `research-hub-auth`; the local
`erdosatlas-workbench/erdosatlas.db` contains only a physics-edge `morphisms`
table (`source_id`/`target_id`), not the morphism registry, and `wrangler` was
unavailable in the capture environment.

**Consequence.** Do not treat 37 as the size of the atlas. If your evaluation
reports "the corpus is thin", that may be an artefact of this gap rather than a
property of the work. Report coverage-sensitive findings as conditional on it.

**Owner action.** Either make the route return all records, or correct the health
count, or state in the API docs why they differ.

## 2. Physics objects are captured only by reachability

`/api/health` declares `physics: 66`. The snapshot holds **20**, because objects
were collected only if a captured morphism referenced them. There is no physics
listing endpoint: `/api/physics`, `/api/objects/physics` and `/api/physics/top`
all return 404.

This is a capture limitation, not evidence that 46 objects are unused.

## 3. There is no full problem catalogue

`/api/problems/top?n=N` caps at 100 regardless of N. `n=6000` still returns 100.
`/api/problems` returns 404. So `snapshot/problems_top100.json` is the top 100 by
solvent index, not the 5,496 problems the health endpoint declares.

## 4. Access documentation is stale

`ACCESS.md` in the private workbench states that
`/data/workbench/{problems,morphisms,embeddings_3d,physics_rich}.json` are public
with no authentication. They now return **HTTP 302** redirecting to
`erdosatlas-private.dev-ef7.workers.dev`. Either un-gate them or update the doc.
Until then, ignore that claim; this snapshot is built from `/api/*` only.

## 5. `strength` does not have one meaning

Across the 37 captured records, `strength` takes values including `proved`,
`conjectured` and `partial`. In at least one record (`mr-001`, a Sidon/radar
correspondence) `proved` appears to credit classical results — Sidon 1938,
Singer 1938 — rather than assert that a cross-domain transfer has been
established.

This ambiguity is not corrected in the claims register, deliberately: resolving
it is part of the evaluation. The rubric's Axis 3 exists for exactly this.

## 6. Citations are unverified at capture

Every claim carries `citations_verified: false`. The capture recorded what each
record cites; it did not open the sources. Treat every citation as a lead to
check, never as established.

## 7. Written by the authors of the subject

This substrate was produced by the same organisation that produced the atlas.
The scope choices — what to include, which traps to warn about — are therefore
contested. Where possible, prefer your own reading of `snapshot/morphisms.json`
over the framing in these documents.
