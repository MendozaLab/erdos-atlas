# Known issues in this substrate

Read this before drawing conclusions. These are defects in the capture or in the
upstream API, not in your evaluation. Each one is reproducible.

## 1. The health count cannot be reconciled with the served data

`/api/health` declares `morphisms: 92`. The snapshot captured **37 records**,
covering **34 distinct (math_id, physics_id) pairs** over 23 problems.

How it was measured: `/api/morphisms/<id>` was queried for every id in `1..6000`.
Twenty-three problem ids returned records. Spot checks at 6001, 7000, 9000 and
12000 returned zero, so the sweep range is not the binding constraint. Both
morphism families are served by the same route and both are captured: 11 curated
(`mr-*`) and 26 generated (`MOR-*`), so this is not a case of a second route
hiding records.

What is *not* established is data loss. Three explanations remain live and this
capture cannot separate them:

1. `92` counts rows including historical or superseded versions. The records
   carry several creation batches (`h2_session_2026-03-29`, `h2_session_2026-04-01`,
   `h2_chimera_2026-04-16`, `agent`, …), so duplicates across sessions are
   plausible. In that case 34 pairs is the real current set and only the counter
   is loose.
2. `92` counts a table this route does not serve, such as the physics-edge
   `morphisms` table. Locally that table holds 54,203 rows, so it is not a
   straight count of that either.
3. About 55 records genuinely exist and are unreachable through the public
   routes.

The authoritative source is `atlas_morphism_records` in D1 `research-hub-auth`.
It was not reachable at capture time: the local `erdosatlas-workbench/erdosatlas.db`
holds only physics edges, and `wrangler` was unavailable.

**Consequence, stated narrowly.** This does not block evaluating any individual
claim — each of the 37 stands or falls on its own record. It does block claims
*about the corpus*, because those need a defensible denominator and there isn't
one. If you find that 28 of 37 are `conjectured`, that speaks for the 37 and not
for the atlas.

Use 34 distinct pairs, not 92, as the denominator, and say so explicitly.

**Owner action.** Either reconcile the counter with what the route serves, or
document why they differ. Option 1 needs no API change beyond honesty in
`/api/health`.


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
