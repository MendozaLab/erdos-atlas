#!/usr/bin/env python3
"""Normalise the frozen atlas snapshot into blind Atlas 2 items.

Reads ONLY from ../snapshot/morphisms.json (frozen, never written) and emits:
  items/atlas2_items.json   blind items, six fields, opaque ids
  items/atlas2_labels.json  private labels keyed by item_id

Everything that could leak the class is removed: strength, citations, evidence
notes, similarity scores, record ids, physics/math ids, authoring session, and
inline problem numbers such as "(#114)".

Deterministic: item ids derive from content, ordering is sorted, and re-running
is byte-identical. The script asserts that on every run.

Usage:
    python3 atlas2/tools/normalise_items.py
"""

import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "snapshot" / "morphisms.json"
OUT_DIR = ROOT / "atlas2" / "items"

FIELDS = ["math_object", "math_invariant", "physics_object",
          "physics_invariant", "transfer_operator", "breakdown_boundary"]

# Patterns that must not survive normalisation.
LEAK_PATTERNS = [
    (re.compile(r"\bPhysics similarity\s*[0-9.]+", re.I), ""),
    (re.compile(r"\bSimilarity\s*[0-9.]+\.?", re.I), ""),
    (re.compile(r"\bEXP-[A-Z0-9-]+"), ""),
    (re.compile(r"\bMOR-[A-Z0-9-]+"), ""),
    (re.compile(r"\bmr-\d+"), ""),
    (re.compile(r"\(\s*#\s*\d+\s*\)"), ""),        # "(#114)"
    (re.compile(r"Erd[oő]s\s+problem\s*#?\s*\d+", re.I), "the problem"),
    (re.compile(r"\bjob-[a-z0-9-]+"), ""),
]


def clean(text):
    if not text:
        return ""
    s = str(text)
    for pat, rep in LEAK_PATTERNS:
        s = pat.sub(rep, s)
    s = s.replace("\u2026", "...")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^[\s,;:.\-]+", "", s)             # leading punctuation after stripping
    s = re.sub(r"\s+,", ",", s)
    return s


def item_id(record, idx):
    """Opaque and content-derived: carries no class, no author, no record id."""
    basis = "|".join(clean(record.get(f, "")) for f in FIELDS)
    return "atlas_" + hashlib.sha256(basis.encode()).hexdigest()[:10]


def build():
    flat = json.loads(SNAPSHOT.read_text())["flat"]
    items, labels = [], []
    seen = {}
    for rec in flat:
        physics_object = rec.get("physics_object") or rec.get("physics_name") or ""
        src = dict(rec)
        src["physics_object"] = physics_object
        iid = item_id(src, len(items))
        if iid in seen:                       # duplicate content: keep one, note the other
            continue
        seen[iid] = True
        item = {"item_id": iid}
        for f in FIELDS:
            item[f] = clean(src.get(f, ""))
        items.append(item)
        labels.append({
            "item_id": iid,
            "class": "atlas",
            "kind": "unknown",
            "crossing_result": None,
            "authored_by": rec.get("created_by") or "unknown",
            "source_record_id": rec.get("id"),
            "shuffle_variant": None,
            "private_split": False,
            "canary": None,
        })
    items.sort(key=lambda x: x["item_id"])
    labels.sort(key=lambda x: x["item_id"])
    return items, labels


def verify_no_leaks(items):
    bad = []
    for it in items:
        blob = " ".join(it[f] for f in FIELDS)
        if re.search(r"\b(MOR-|mr-\d|EXP-|similarity)\b", blob, re.I):
            bad.append(it["item_id"])
        if re.search(r"\b\d{4}-\d{2}-\d{2}\b", blob):
            bad.append(it["item_id"])
    return sorted(set(bad))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items, labels = build()

    leaks = verify_no_leaks(items)
    if leaks:
        print(f"FAIL: {len(leaks)} items still carry leak patterns: {leaks[:5]}", file=sys.stderr)
        return 1

    payload = {"count": len(items), "schema": "atlas2/item.schema.json", "items": items}
    label_payload = {"count": len(labels), "schema": "atlas2/label.schema.json", "labels": labels}

    ip = OUT_DIR / "atlas2_items.json"
    lp = OUT_DIR / "atlas2_labels.json"
    ip.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    lp.write_text(json.dumps(label_payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n")

    # Determinism: rebuild and compare bytes.
    items2, labels2 = build()
    ip2 = json.dumps({"count": len(items2), "schema": payload["schema"], "items": items2},
                     indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if ip2 != ip.read_text():
        print("FAIL: normalisation is not deterministic", file=sys.stderr)
        return 1

    print(f"items written: {len(items)}  -> {ip.relative_to(ROOT)}")
    print(f"labels written: {len(labels)} -> {lp.relative_to(ROOT)}")
    print("determinism: byte-identical on re-run")
    empty = [i["item_id"] for i in items if not i["transfer_operator"]]
    print(f"items with empty transfer_operator: {len(empty)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
