# Unversioned patches

Two source files I modified live inside directories that are **gitignored**, so
the edits are not in any repository and would be lost if the working copy were
replaced. The patches are recorded here so they survive and can be reapplied.

This is not ideal. The real fix is to bring these directories under version
control; until then, this file is the only durable record.

---

## 1. `erdos-mdl-mapper/scripts/embed_fc_statements.py`

Path is ignored by `Math-Problems/.gitignore` line 2 (`erdos-mdl-mapper/scripts/`).

**Why.** The script hardcoded `PROVIDER = "deepmind-statements"`, a provider the
query path never reads. Running it as written produced vectors nothing served —
which is how the 440-row dead layer at `deepmind-statements` came to exist. The
live path uses `provider='leandojo'` and index `erdosatlas-leandojo`.

**Patch.** Add a `--provider` flag and use it in the generated SQL and metadata.

Before, in `main()`:

```python
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()
```

After:

```python
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--provider", default=PROVIDER,
                    help=f"atlas_vectors.provider value (default {PROVIDER}). "
                         "Use 'leandojo' to refresh the provider the API actually queries.")
    args = ap.parse_args()
    provider = args.provider
```

Then replace two uses of the constant with the variable:

```python
# before
f"('erdos-{r['problem_number']}', '{PROVIDER}', 'problem', {DIM}, "
"metadata": {**e["metadata"], "provider": PROVIDER},

# after
f"('erdos-{r['problem_number']}', '{provider}', 'problem', {DIM}, "
"metadata": {**e["metadata"], "provider": provider},
```

`PROVIDER` remains the default so existing invocations are unchanged.

**Applied** 2026-11-10: re-embedded 1,011 statements with `--provider leandojo`,
wrote 41 D1 batches, enqueued index upsert `d3939945`.

---

## 2. `erdosatlas-workbench/erdosatlas-api-worker.js`

This one **is** version controlled — committed as `b2de9d24`. Listed here only so
the deploy state and the source agree: the deployed worker is
`edf3e5f7-7b74-4560-a879-33cc8bcec38b`.

---

## 3. Data files (not patches)

Modified on disk but untracked, so nothing to commit:

- `erdos-mdl-mapper/data/erdos_problems.db` — refreshed by
  `lean_filesystem_audit.py --reconcile` (675 → 846 rows). Backup of the
  pre-reconcile state preserved at
  `/Users/kenbengoetxea/container-projects/backups/erdos_problems.pre_reconcile_2026-11-10.db`.
