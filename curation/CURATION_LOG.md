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
