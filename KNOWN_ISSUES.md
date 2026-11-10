# Known issues in this substrate

Read this before drawing conclusions. These are defects in the capture or in the
upstream API, not in your evaluation. Each one is reproducible.

## 1. Nineteen records are held in the database but not served

Verified against D1 `research-hub-auth.atlas_morphism_records` on 2026-11-10:

| | count |
|---|---|
| records in the table | 90 (was 92; two placeholders deleted, see `DATA_DEFECTS.md`) |
| reachable via `/api/morphisms/:id` | 71 |
| held but not served | 19 |

The 19 are not scattered. They sit on ten math ids whose values are **not
numeric**:

```
AIM-045  AIM-067  AIM-072  MW-037  MW-054
SIM-003  SIM-004  SMA-007  SMA-010  SMA-011
```

Those ids have rows in the table and return an empty list from the route. Every
numeric id resolves. So the defect is narrow: the route handles numeric ids only,
and non-numeric problem ids are silently invisible.

**An earlier claim in this repository was wrong and is retracted.** A first
capture swept numeric ids 1..6000 and reported 37 of 92, and this file then
suggested roughly 55 records were unreachable. That was a measurement error: the
numeric id space runs to about 80590, and 31 problems with morphisms sit in the
50184..80590 range, invisible to a sweep capped at 6000. Extending the probe
raised the capture from 37 to 71. The residue is the 19 above.

**Consequence.** The denominator for any corpus-level finding is **71 served
claims** over 54 problems, or **90** if you also count the unserved 19. State
which you used. Individual claims are unaffected either way.

**Owner action.** Make the route resolve non-numeric math ids, or document that
it does not, or move those records to numeric ids. Nineteen silent records is a
small enough set to fix properly.

## 2. Physics objects are captured only by reachability

`/api/health` declares `physics: 66`. The snapshot holds **39**, because objects
were collected only if a captured morphism referenced them. There is no physics
listing endpoint: `/api/physics`, `/api/objects/physics` and `/api/physics/top`
all return 404.

This is a capture limitation, not evidence that the other 27 objects are unused.

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
