# Known issues in this substrate

Read this before drawing conclusions. These are defects in the capture or in the
upstream API, not in your evaluation. Each one is reproducible.

## 1. FIXED 2026-11-10 — the route dropped non-numeric math ids

`/api/morphisms/:id` matched `^\d+$`, so any math id that was not all digits
returned nothing. Ten ids were affected:

```
AIM-045  AIM-067  AIM-072  MW-037  MW-054
SIM-003  SIM-004  SMA-007  SMA-010  SMA-011
```

Those ten ids held **19 records** that existed in `atlas_morphism_records` and
were invisible to every API consumer. The pattern now accepts
`[A-Za-z0-9_.-]+`, all ten resolve, and the snapshot captures **90 of 90**
declared morphisms — previously 71.

Two earlier claims in this repository were wrong and are retracted rather than
quietly edited:

1. A first capture reported 37 of 92 and suggested ~55 records were unreachable.
   The cause was a sweep capped at numeric id 6000 while the id space runs to
   ~80590, hiding 31 problems. That was a measurement error, not an API defect.
2. A second pass blamed 19 records on "non-numeric ids the route will not
   resolve" and treated that as an API limitation to be documented. It was a
defect to be fixed, and it has been.

The denominator is now simply **90 claims over 64 problems**. No caveat needed.

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

Across the 90 captured records, `strength` takes values including `proved`,
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
