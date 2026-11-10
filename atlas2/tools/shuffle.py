#!/usr/bin/env python3
"""Generate shuffled negatives for Atlas 2.

A shuffled item takes one record's mathematical side and another record's physical
side, so the pair is incoherent by construction. That makes it a chance baseline
rather than a hard test, which is why the unconstrained variant is generated last
and used only as an easy control.

Variants, hardest first:
  same_category      swap between records whose physics share a category, so the
                     mismatch is not obvious on the surface
  adjacent_domain    swap within the same mathematics domain
  field_permutation  same record, mathematical and physical invariants exchanged;
                     isolates whether a reviewer reads content or shape
  random             any two records; easy control, not the headline null

Deterministic: pairs are chosen from a seeded RNG in sorted record order.

Usage:
    python3 atlas2/tools/shuffle.py
"""

import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from normalise_items import ROOT, SNAPSHOT, clean, item_id  # noqa: E402

OUT = ROOT / "atlas2" / "items"
SEED = 20261110


def load():
    flat = json.loads(SNAPSHOT.read_text())["flat"]
    recs = []
    for r in flat:
        src = dict(r)
        src["physics_object"] = r.get("physics_object") or r.get("physics_name") or ""
        recs.append((item_id(src, 0), src))
    seen, uniq = set(), []
    for iid, src in recs:
        if iid in seen:
            continue
        seen.add(iid)
        uniq.append((iid, src))
    uniq.sort(key=lambda x: x[0])
    return uniq


def make(a, b, iid, variant, cls="shuffled", labels=None):
    item = {"item_id": iid}
    item["math_object"] = clean(a["math_object"])
    item["math_invariant"] = clean(a["math_invariant"])
    item["physics_object"] = clean(b["physics_object"])
    item["physics_invariant"] = clean(b["physics_invariant"])
    item["transfer_operator"] = clean(a["transfer_operator"])
    item["breakdown_boundary"] = clean(a["breakdown_boundary"])
    if labels is not None:
        labels.append({
            "item_id": iid, "class": cls, "kind": "none",
            "crossing_result": None, "authored_by": "generator",
            "source_record_id": a.get("id"), "shuffle_variant": variant,
            "private_split": False, "canary": None,
            "donor_record_id": b.get("id"),
        })
    return item

def pair_up(uniq, keyfn, variant, rng, items, labels):
    groups = {}
    for iid, src in uniq:
        groups.setdefault(keyfn(src), []).append((iid, src))
    used = set()
    for key in sorted(groups, key=str):
        members = list(groups[key])
        if len(members) < 2:
            continue
        members.sort(key=lambda x: x[0])
        rng.shuffle(members)
        for (ia, a), (ib, b) in zip(members[0::2], members[1::2]):
            if ia in used or ib in used:
                continue
            used.update({ia, ib})
            iid = f"shuf_{variant}_{ia[6:8]}{ib[6:8]}"
            items.append(make(a, b, iid, variant, labels=labels))


def field_permutation(uniq, items, labels):
    for iid, src in uniq:
        item = {"item_id": f"shuf_perm_{iid[6:]}"}
        item["math_object"] = clean(src["math_object"])
        item["math_invariant"] = src["physics_invariant"]
        item["physics_object"] = clean(src["physics_object"])
        item["physics_invariant"] = src["math_invariant"]
        item["transfer_operator"] = clean(src["transfer_operator"])
        item["breakdown_boundary"] = clean(src["breakdown_boundary"])
        items.append(item)
        labels.append({
            "item_id": item["item_id"], "class": "shuffled", "kind": "none",
            "crossing_result": None, "authored_by": "generator",
            "source_record_id": src.get("id"),
            "shuffle_variant": "field_permutation",
            "private_split": False, "canary": None,
        })


def random_pairs(uniq, rng, items, labels, n=40):
    pool = list(uniq)
    rng.shuffle(pool)
    for k in range(0, min(len(pool) - 1, n), 2):
        ia, a = pool[k]
        ib, b = pool[k + 1]
        items.append(make(a, b, f"shuf_rand_{ia[6:8]}{ib[6:8]}", "random", labels=labels))


def main():
    uniq = load()
    rng = random.Random(SEED)
    items, labels = [], []
    pair_up(uniq, lambda s: s.get("category") or "none", "same_category", rng, items, labels)
    pair_up(uniq, lambda s: (s.get("math_object") or "")[:12], "adjacent_domain", rng, items, labels)
    field_permutation(uniq, items, labels)
    random_pairs(uniq, rng, items, labels)
    items.sort(key=lambda x: x["item_id"])
    labels.sort(key=lambda x: x["item_id"])

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "atlas2_shuffled.json").write_text(json.dumps(
        {"count": len(items), "schema": "atlas2/item.schema.json", "items": items},
        indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    (OUT / "atlas2_shuffled_labels.json").write_text(json.dumps(
        {"count": len(labels), "labels": labels},
        indent=2, ensure_ascii=False, sort_keys=True) + "\n")

    from collections import Counter
    print(f"shuffled items: {len(items)}")
    for k, v in sorted(Counter(l["shuffle_variant"] for l in labels).items()):
        print(f"  {k:18s} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
