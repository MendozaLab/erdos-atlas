#!/usr/bin/env python3
"""Pin a dated, immutable snapshot of the public ErdosAtlas API.

The API exposes no global listing of morphisms or physics objects, so the
exporter discovers them by sweeping problem ids. Every count it reports is
reconciled against /api/health, and anything it could not reach is recorded as
a gap rather than silently omitted.

Usage:
    python3 tools/snapshot.py --out snapshot --max-id 6000 --workers 32
"""

import argparse
import concurrent.futures
import hashlib
import json
import pathlib
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE = "https://erdosatlas-api.dev-ef7.workers.dev"


def get(path, timeout=25):
    """Return (status, parsed-json-or-None). Never raises on HTTP errors."""
    url = BASE + path
    req = urllib.request.Request(url, headers={"User-Agent": "erdos-atlas-eval-snapshot"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return None, None


def fetch_morphisms(pid):
    status, body = get(f"/api/morphisms/{pid}")
    if status != 200 or not isinstance(body, dict):
        return pid, []
    return pid, body.get("morphisms", []) or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="snapshot")
    ap.add_argument("--max-id", type=int, default=81000,
                    help="numeric id ceiling for a public-only sweep (ids run to ~80590)")
    ap.add_argument("--ids-file", default=None,
                    help="explicit id list, one per line; overrides --max-id")
    ap.add_argument("--workers", type=int, default=32)
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print("health ...", flush=True)
    _, health = get("/api/health")
    declared = {row["t"]: row["n"] for row in (health or {}).get("counts", [])}

    print("top problems ...", flush=True)
    _, top = get("/api/problems/top?n=100")
    problems = (top or {}).get("problems", [])

    if args.ids_file:
        ids = [ln.strip() for ln in pathlib.Path(args.ids_file).read_text().splitlines() if ln.strip()]
        print(f"probing {len(ids)} ids from {args.ids_file} ...", flush=True)
    else:
        ids = list(range(1, args.max_id + 1))
        print(f"sweeping numeric ids 1..{args.max_id} for morphisms ...", flush=True)

    by_math = {}
    unserved = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for pid, ms in ex.map(fetch_morphisms, ids):
            if ms:
                by_math[str(pid)] = ms
            else:
                unserved.append(str(pid))

    morphisms = [m for ms in by_math.values() for m in ms]
    phys_ids = sorted({m.get("physics_id") for m in morphisms if m.get("physics_id")})
    print(f"  {len(morphisms)} morphisms over {len(by_math)} problems, "
          f"{len(phys_ids)} distinct physics ids", flush=True)

    print("physics objects ...", flush=True)
    physics = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(get, f"/api/query/physics/{p}"): p for p in phys_ids}
        for f in concurrent.futures.as_completed(futs):
            p = futs[f]
            status, body = f.result()
            if status == 200 and isinstance(body, dict):
                physics[p] = body.get("physics_object") or body

    payloads = {
        "morphisms.json": {
            "source": BASE + "/api/morphisms/<id>",
            "by_math_id": by_math,
            "flat": morphisms,
        },
        "unserved_ids.json": {
            "note": "ids probed that returned no morphisms; non-numeric ones indicate records "
                    "held in the database but not reachable through this route",
            "count": len(unserved),
            "ids": unserved,
        },
        "problems_top100.json": {"source": BASE + "/api/problems/top?n=100", "problems": problems},
        "physics_objects.json": {"source": BASE + "/api/query/physics/<id>", "objects": physics},
    }
    hashes = {}
    for name, obj in payloads.items():
        raw = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False).encode()
        (out / name).write_bytes(raw)
        hashes[name] = hashlib.sha256(raw).hexdigest()

    manifest = {
        "snapshot_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "api_base": BASE,
        "method": "per-id probe for morphisms; union of physics_id fields for objects",
        "id_probe": {
            "source": args.ids_file or f"numeric sweep 1..{args.max_id}",
            "ids_probed": len(ids),
            "ids_with_morphisms": len(by_math),
            "ids_without": len(unserved),
        },
        "declared_counts_health": declared,
        "captured": {
            "morphisms": len(morphisms),
            "problems_with_morphisms": len(by_math),
            "problems_top100": len(problems),
            "physics_objects": len(physics),
        },
        "reconciliation": {
            "morphisms_declared": declared.get("morphisms"),
            "morphisms_captured": len(morphisms),
            "physics_declared": declared.get("physics"),
            "physics_captured": len(physics),
        },
        "known_gaps": [
            "The API exposes no full problem catalogue; only the top 100 by solvent index.",
            "Morphisms are discoverable only per problem id. A numeric sweep must reach ~80590; "
            "an earlier capture capped at 6000 and missed 31 problems in the 50184..80590 range.",
            "Records whose math_id is non-numeric (AIM-*, MW-*, SIM-*, SMA-*) are held in the "
            "database but return nothing from /api/morphisms/:id; see unserved_ids.json.",
            "physics_objects counts objects reachable from captured morphisms, not all declared objects.",
        ],
        "sha256": hashes,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {len(payloads) + 1} files to {out}/")
    print(json.dumps(manifest["reconciliation"], indent=2))


if __name__ == "__main__":
    main()
