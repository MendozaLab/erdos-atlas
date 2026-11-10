# Curation log

Changes made to production data, with the evidence for each. Backups are in
`curation/`.

## 2026-11-10 — D1 and D3 from `DATA_DEFECTS.md`

Target: D1 `research-hub-auth`, table `atlas_morphism_records`.
Operator: local session via `wrangler d1 execute --remote`.
Backup of every affected row, taken before any write: `curation/PRE_CURATION_BACKUP.json`
(7 rows, full records).

### D1 — deleted two placeholder records

```sql
DELETE FROM atlas_morphism_records
WHERE evidence LIKE '%test morphism%'
  AND math_object IS NULL
  AND transfer_operator IS NULL
  AND breakdown_boundary IS NULL;
```

`changes: 2`.

Guarded three ways so it could only match the placeholders: the marker string,
plus the two nulls that made them non-claims. Both deleted ids are preserved in
the backup:

```
MOR-114-PHYS-PT-001-1775139177870
MOR-114-PHYS-PT-001-1775139177883
```

### D3 — marked five incomplete records

No status column existed, so one was added additively rather than overloading
`strength` (which describes confidence, not completeness):

```sql
ALTER TABLE atlas_morphism_records ADD COLUMN record_status TEXT DEFAULT 'active';
UPDATE atlas_morphism_records SET record_status = 'incomplete'
WHERE transfer_operator IS NULL OR transfer_operator = ''
   OR breakdown_boundary IS NULL OR breakdown_boundary = '';
```

`changes: 5`.

Marked:

```
MOR-96-PHYS-C-004-1776365646328
MOR-97-PHYS-CL-003-1776365647253
MOR-389-PHYS-R-002-1776364597284
MOR-396-PHYS-R-002-1776364596453
MOR-505-PHYS-F-001-1776365642682
```

`alter` reported `changes: 0`, which is expected: D1 counts DML rows, not schema
changes. The update then matched exactly five rows, the number predicted from the
pre-write audit.

### Before and after

| Measure | before | after |
|---|---|---|
| rows in table | 92 | 90 |
| placeholder rows | 2 | 0 |
| incomplete (`record_status`) | n/a | 5 |
| active | 92 | 85 |

### Verification

Checked end to end through the public API, not just the database:

- `/api/health` now reports `morphisms: 90` (was 92).
- `/api/morphisms/114` returned 6 records before, 4 after. The two placeholders
  are gone; `mr-009`, `mr-011`, `morph-unitarity-114-kepler` and
  `morph-unitarity-114-carnot` remain.

### What this did not do

- No surviving row had any existing field modified. The only schema change is the
  additive `record_status` column, which is nullable with a default.
- **The API does not yet expose `record_status`.** The marking exists in the
  database; surfacing it requires a worker change and a deploy, which was not
  part of this task. Until then the five records are still served as if active.

### Side effect worth recording

Investigating why the API seemed to serve 40% of its records showed the cause was
a capture cap, not the API. See `KNOWN_ISSUES.md` §1 for the retraction: the
numeric id space runs to ~80590, and the earlier sweep stopped at 6000. The
snapshot has been rebuilt from the authoritative id list and now captures 71 of
90, with the remaining 19 identified as records on non-numeric math ids.

## 2026-11-10 — atlas formalization refresh

Added `atlas_formalization_coverage` (1,011 rows) and inserted 16 Erdős problems
(1201-1221, non-contiguous) that formal-conjectures now covers but the catalogue
lacked. Applied with `wrangler d1 execute --file`, `changes: 1028`.

Full method, counts and queries: `FORMALIZATION_REFRESH_2026-11-10.md`.
Reproduction SQL: `atlas_formalization_refresh_2026-11-10.sql`.

Both statements are idempotent — the coverage table is cleared and refilled, and
the problem inserts use `INSERT OR IGNORE` so no existing row can be overwritten.

No `math_status` value was changed. Upstream's `research solved` marks solved
variants; `math_status` records the mathematical status of the main problem.
Treating one as evidence for the other would have corrupted the catalogue.

## 2026-11-10 — evidence split, refuted filter, non-numeric id resolver

Three defects closed in the API and database.

**C1 (D2) evidence split.** Added `citations` and `evidence_note` columns to
`atlas_morphism_records` and backfilled: 13 rows carry a citation list, 77 carry a
prose note. `evidence` retained for compatibility. Because the route selects
`mr.*`, both new columns were exposed without a deploy.

**C3 record_status exposure.** Also automatic via `mr.*`; the five incomplete
records now return `record_status: incomplete`.

**C2 non-numeric ids.** The route pattern was `^\d+$`, so `AIM-045` and nine
siblings returned nothing. Widened to `[A-Za-z0-9_.-]+`. All ten now resolve and
the 19 records they held are reachable — total served coverage went 71 -> 90 of 90.

**C5 refuted filter.** `refuted-locally` records are excluded from default
results and returned under `?include=refuted`.

### Deploy incident, recorded

The first deploy of C2/C5 returned HTTP 500 (worker error 1101) on every
`/api/morphisms/*` request. Cause: I used `urlParams`, which is not in scope in
that block; `url` is. `health` stayed green, so only a direct probe caught it.
Fixed and redeployed within the same session; verified 200 before moving on.
Lesson: probe the changed route itself, not just `/api/health`.

Worker version: `edf3e5f7-7b74-4560-a879-33cc8bcec38b` (config `wrangler-api.toml`).

### Verification

```
AIM-045 2  AIM-067 2  AIM-072 2  MW-037 2  MW-054 2
SIM-003 2  SIM-004 2  SMA-007 1  SMA-010 2  SMA-011 2   = 19 records restored
/api/morphisms/166              -> 1 (conjectured)
/api/morphisms/166?include=refuted -> 2 (refuted-locally, conjectured)
```

## 2026-11-10 — vector refresh and Lean registry reconcile

**C4 vector staleness.** The live search path reads `atlas_vectors`
(provider=`leandojo`) and queries index `erdosatlas-leandojo`. Both dated to
2026-04-15, and the `leandojo` rows carried **no `text_hash` at all** — the
staleness-detection mechanism only ever worked for `deepmind-statements`, a
provider the query path does not read.

Added `--provider` to `embed_fc_statements.py` (it hardcoded the dead provider),
re-embedded all 1,011 formal-conjectures statements, and wrote them as
provider=`leandojo`:

| | before | after |
|---|---|---|
| leandojo rows | 5,596 | 5,629 |
| rows with `text_hash` | 0 | 1,011 |
| newest | 2026-04-15 | 2026-11-10 |

D1 updated in 41 batches; index upsert enqueued for 1,011 vectors
(mutation `d3939945`). Verified `/api/query/math/30` returns 20 semantic matches
and `/api/query/invariant?q=sidon` returns 10 math + 5 physics.

Remaining and deliberate: 4,618 non-FC `leandojo` vectors are still April-era and
hashless. Refreshing them needs statement text for the whole corpus, not just the
formal-conjectures subset.

**C6 Lean registry.** `lean_filesystem_audit.py` writes local
`erdos_problems.db :: lean_proofs`, not D1 `lean_proof_registry`. It had not run
since March partly because **it cannot run on the default Python 3.9** — it uses
`int | None` annotations. Ran it under pyenv 3.11.6.

Reconcile: 675 -> 846 rows, 100 -> 115 problems, 744 rows now carry
`fs_content_hash`, 616 resolve to existing files. Best-of-breed: 67 CLEAN,
7 one-sorry, 3 NEAR, 37 ARCHITECTURE.

Backfilled `fs_content_hash` into D1 `lean_proof_registry` for the 10 rows that
match the local scan by (problem_id, file_name); 493 -> 499 hashed.

**A near-miss worth recording.** I nearly marked the other 64 unhashed rows
`GHOST_NO_FILE`. Spotlight shows those `DDC_Aristotle_*.lean` files exist — the
scan keys on problem-id-in-path and those filenames do not encode one, so the
scan never saw them. Marking them missing would have been false.

The registry remains a *publication ledger* (zenodo_doi, arxiv_id, proof_grade,
portfolio_tier) that a filesystem scan cannot derive, and it is still served by
nothing. Consolidation with `scoring_lean_artifacts` is a design decision, not a
maintenance task, and is deliberately not attempted here.

**Environment findings.** `~/.cache/huggingface/hub` is a symlink into
`/Volumes/2024_18tb/...` which is not mounted; embedding needed
`HF_HOME=/tmp/hf-home`. The external drive being absent will break any future
run of the embedding pipeline until it is remounted or the env var is set.
