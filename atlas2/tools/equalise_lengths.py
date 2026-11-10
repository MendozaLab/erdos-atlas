#!/usr/bin/env python3
"""TESTED AND INSUFFICIENT — do not rely on this tool as the leak fix.

Measured on 2026-11-10 by sweeping the cap and re-scoring author separation from
lengths alone:

    cap   retained text   length-AUC
     40           100%        0.996
     22           100%        0.996
     16            99%        0.996
     12            97%        0.994
      8            78%        0.994
      5            54%        1.000

Truncating to five words per field, which keeps barely half the text, does not move
the classifier at all. The fingerprint is the *per-field length profile* — which
fields are short, which are long, which are empty — and that profile survives
truncation because it is a shape, not a total.

The conclusion is in PREREGISTRATION.md: length control has to happen when new
classes are authored, not afterwards. This tool is retained because the negative
result is worth reproducing, not because it solves anything.

Equalise field lengths so prose shape stops identifying the author.

The gate measured field lengths alone separating authoring sessions at AUC 1.000.
Two honest options exist:

  1. Require authors of new classes (gold, decoy) to hit per-field word targets, so
     classes are length-matched by construction.
  2. Cap the frozen items at the same targets, accepting that content is truncated.

This script does (2), because the existing 82 items are frozen and cannot be
rewritten. Truncation is lossy and that is stated plainly rather than hidden: what
survives is the six fields' content up to the cap, and the trailing clause that
gets cut is gone.

Caps are per field, not global, because the fields differ in how much text they
need. A hard cap makes most fields exactly the cap length, which collapses the
variance the classifier was reading.

Usage:
    python3 atlas2/tools/equalise_lengths.py
"""

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from normalise_items import FIELDS, ROOT  # noqa: E402

SRC = ROOT / "atlas2" / "items" / "atlas2_items.json"
LABELS = ROOT / "atlas2" / "items" / "atlas2_labels.json"
OUT_ITEMS = ROOT / "atlas2" / "items" / "atlas2_items_eq.json"
OUT_LABELS = ROOT / "atlas2" / "items" / "atlas2_labels_eq.json"

# Per-field word caps. Tuned so the cap sits below the median of the frozen corpus,
# which is what removes the between-author spread rather than merely shrinking it.
CAPS = {
    "math_object": 8,
    "math_invariant": 18,
    "physics_object": 8,
    "physics_invariant": 18,
    "transfer_operator": 22,
    "breakdown_boundary": 18,
}


def truncate(text, cap):
    """Cut to `cap` words on a word boundary, dropping a trailing partial clause."""
    words = str(text or "").split()
    if len(words) <= cap:
        return " ".join(words)
    cut = " ".join(words[:cap]).rstrip(",;:-")
    # drop a dangling connective so the stumps do not read as truncated
    cut = re.sub(r"\b(and|or|the|a|an|of|to|in|at|by|with|that|which|is|are)$", "", cut).strip()
    return cut.rstrip(",;:-. ")


def main():
    items = json.loads(SRC.read_text())["items"]
    labels = json.loads(LABELS.read_text())["labels"] if LABELS.exists() else []

    out = []
    for it in items:
        eq = {"item_id": it["item_id"]}
        for f in FIELDS:
            eq[f] = truncate(it.get(f, ""), CAPS[f])
        out.append(eq)

    OUT_ITEMS.write_text(json.dumps(
        {"count": len(out), "schema": "atlas2/item.schema.json",
         "equalisation": {"caps": CAPS, "method": "per-field word cap, trailing clause dropped"},
         "items": out}, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    if labels:
        OUT_LABELS.write_text(json.dumps({"count": len(labels), "labels": labels},
                                         indent=2, ensure_ascii=False, sort_keys=True) + "\n")

    import collections
    import statistics
    print(f"equalised items: {len(out)}  caps={CAPS}")
    for f in FIELDS:
        n = [len(x[f].split()) for x in out]
        print(f"  {f:20s} mean={statistics.mean(n):5.1f} sd={statistics.pstdev(n):4.1f} "
              f"min={min(n)} max={max(n)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
