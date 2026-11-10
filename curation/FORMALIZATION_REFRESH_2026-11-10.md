# Atlas formalization refresh — 2026-11-10

Brings the atlas's record of formal-conjectures progress up to date. The atlas's
own Lean registry (`lean_proof_registry`) had not been touched since
**2026-06-09**, five months earlier, and the atlas had no per-problem record of
*upstream* formalization coverage at all — it knew about local proof artifacts and
nothing about what the public corpus had gained.

## What upstream had accumulated

Measured against `google-deepmind/formal-conjectures` at
`f80a76e9896b8288affb32b76a20f24ef22de05a`:

| Measure | Value |
|---|---|
| commits since 2026-06-09 | 1,596 |
| of those touching `ErdosProblems/` | 887 |
| `ErdosProblems/*.lean` files | 1,012 |
| problems with ≥1 `@[category research solved]` | 818 |
| total solved declarations | 1,988 |

The atlas's `math_status` field means the *mathematical* status of the main
problem, sourced from erdosproblems.com. Upstream's `research solved` marks solved
*variants*. These are different quantities, so no status was rewritten on the
strength of the other — conflating them would have corrupted the catalogue.

## What was added

**A new table, `atlas_formalization_coverage`**, one row per formalized problem
(1,011 rows), pinned to the upstream commit:

```sql
problem_id, upstream_commit, file_path,
solved_decl_count, open_decl_count, sorry_line_count, checked_at
```

Counts come from `git grep -c` over the pinned tree. `sorry_line_count` is a
line-level occurrence count, not a parsed obligation count — treat it as a rough
depth signal, not a proof-quality measure.

**16 missing problems**, ids 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1209, 1210,
1211, 1212, 1213, 1214, 1217, 1219, 1221. formal-conjectures now covers Erdős
problems past the atlas's 1,200 ceiling, and those problems did not exist in the
catalogue at all. Inserted with the catalogue's own conventions (`title: 'Erdős
Problems'`, `collection: 'erdos'`), `math_status: 'open'` to match neighbouring
rows, and a `notes` field recording provenance and that the status is not
independently verified.

Ids 1208, 1215, 1216, 1218 and 1220 are absent upstream as well, so the numbering
is not a gap in this update.

## Resulting state

| Measure | Before | After |
|---|---|---|
| `atlas_problems` rows | 5,496 | 5,512 |
| Erdős collection | 1,201 | 1,217 |
| `atlas_formalization_coverage` rows | (table absent) | 1,011 |
| Erdos problems with upstream formalization | untracked | 1,011 |
| Erdos problems with no formalization | unknown | 206 |

## What this makes queryable

Coverage against mathematical status, for the Erdős collection:

| `math_status` | problems | with ≥1 solved formalization |
|---|---|---|
| open | 733 | 425 (58%) |
| solved | 368 | 296 (80%) |
| disproven | 116 | 97 (84%) |
| **total** | **1,217** | **818** |

The 425 open problems carrying solved formalized variants are the interesting
row. It is large, and it is the reason the two fields must not be merged: a
problem being open does not mean nothing about it has been formalized, and
reading `math_status` alone would hide most of the corpus's actual progress.

The 206 unformalized problems are the remaining surface — the places where a
formalization would be genuinely new rather than a repeat.

## Reproduce

```bash
# pin
git -C <clone> rev-parse upstream/main     # f80a76e9…
# per-file counts
git -C <clone> grep -c 'category research solved' upstream/main -- FormalConjectures/ErdosProblems
git -C <clone> ls-tree -r --name-only upstream/main -- FormalConjectures/ErdosProblems
# apply
wrangler d1 execute research-hub-auth --remote --file atlas_update.sql
```

## Not done

- `lean_proof_registry` (567 rows, 103 problems) is still stamped 2026-06-09. It
  tracks *local* proof artifacts and needs the filesystem audit
  (`lean_filesystem_audit.py --reconcile`), not this refresh. Left untouched
  rather than half-updated.
- `scoring_lean_artifacts` (22 rows) likewise unchanged.
- The public API does not expose `atlas_formalization_coverage` yet. The data is
  queryable in D1; serving it needs a worker route.
