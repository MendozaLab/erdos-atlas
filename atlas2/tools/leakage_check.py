#!/usr/bin/env python3
"""Leakage gate for Atlas 2. Must pass before any human or model scoring.

The risk this measures: if a classifier can predict a hidden attribute from
surface text alone, then any class split correlated with that attribute will leak
and every downstream number is worthless.

Two feature families, on purpose:

  content  TF-IDF over words and bigrams. Expected to predict physics category —
           that is the pipeline working, not leakage.
  style    character n-grams, stopword frequencies, punctuation and length only,
           with all content words removed. This is the pure fingerprint. If style
           alone predicts the authoring session, the corpus has distinctive
           voices, and items written by different people will be separable by
           prose rather than by correspondence.

Reported per target: cross-validated AUC, the chance baseline, and a permutation
p-value. Nothing here is scored yet; this is a property of the frozen atlas.

Usage:
    python3 atlas2/tools/leakage_check.py
"""

import json
import pathlib
import re
import sys
import collections
import warnings
warnings.filterwarnings("ignore")

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from normalise_items import FIELDS, ROOT, SNAPSHOT  # noqa: E402

import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--items", default="atlas2_items.json", help="filename under atlas2/items/")
ap.add_argument("--labels", default=None, help="defaults to matching *_labels/_eq file")
_ARGS, _ = ap.parse_known_args()

ITEMS = ROOT / "atlas2" / "items" / _ARGS.items
_lab = _ARGS.labels or ("atlas2_labels_eq.json" if _ARGS.items.endswith("_eq.json") else "atlas2_labels.json")
LABELS = ROOT / "atlas2" / "items" / _lab

STOP = set("""a an the of in on at to for from by with without and or not is are was were be been
being that this these those it its as into than then so such which who whom whose what when where
while both each any all no nor only own same very can will just should now""".split())


def text_of(item):
    return " . ".join(item.get(f, "") for f in FIELDS)


def style_text(item):
    """Content-free skeleton: word lengths, punctuation, stopwords only."""
    out = []
    for f in FIELDS:
        s = item.get(f, "")
        words = re.findall(r"[A-Za-z']+", s)
        out.append(" ".join(w.lower() for w in words if w.lower() in STOP))
        out.append(f"len{min(len(words) // 5, 12)}")
        out.append(f"punct{s.count(',') // 2}{s.count(';')}{s.count(':')}")
        out.append("C" if s[:1].isupper() else "c")
    return " ".join(out)


def length_only(item):
    """Nothing but field lengths. If this alone separates the groups, the corpus
    is fingerprinted by brevity rather than by voice, and lengths need equalising
    before any blind scoring."""
    return " ".join(f"w{min(len(item.get(f, '').split()), 40)}" for f in FIELDS)


def auc_from_proba(y, proba, classes):
    if len(classes) > 2:
        return roc_auc_score(y, proba, multi_class="ovr", labels=classes)
    return roc_auc_score(y, proba[:, 1])


def evaluate(X_texts, y, label, n_perm=200, seed=0):
    y = np.asarray(y)
    counts = collections.Counter(y)
    if len(counts) < 2 or min(counts.values()) < 3:
        return None
    n_splits = min(5, min(counts.values()))
    clf = make_pipeline(
        TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True),
        LogisticRegression(max_iter=2000, C=1.0),
    )
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    classes = np.unique(y)

    def score(yy):
        proba = cross_val_predict(clf, X_texts, yy, cv=cv, method="predict_proba")
        return auc_from_proba(yy, proba, np.unique(yy))

    auc = score(y)
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(n_perm):
        try:
            null.append(score(rng.permutation(y)))
        except Exception:
            continue
    p = (1 + sum(1 for v in null if v >= auc)) / (1 + len(null))
    chance = max(counts.values()) / len(y)
    return {"target": label, "auc": float(auc), "chance_acc": float(chance),
            "p": float(p), "n": int(len(y)), "classes": len(classes)}



def main():
    items = {i["item_id"]: i for i in json.loads(ITEMS.read_text())["items"]}
    labels = json.loads(LABELS.read_text())["labels"]
    snap = {str(r.get("id")): r for r in json.loads(SNAPSHOT.read_text())["flat"]}

    rows = []
    for lab in labels:
        it = items.get(lab["item_id"])
        if not it:
            continue
        src = snap.get(str(lab.get("source_record_id"))) or {}
        rows.append((it, lab, src))

    print(f"atlas items: {len(rows)}\n")

    # Target 1 — authoring session, restricted to the two dominant authors so the
    # comparison is balanced and the prediction is a fair binary question.
    counts = collections.Counter(lab["authored_by"] for _, lab, _ in rows)
    top2 = [a for a, _ in counts.most_common(2)]
    sub = [(it, lab, src) for it, lab, src in rows if lab["authored_by"] in top2]
    print(f"target: authored_by  ({top2[0]} vs {top2[1]}, n={len(sub)})")
    for fam, fn in (("content", text_of), ("style", style_text), ("length", length_only)):
        r = evaluate([fn(it) for it, _, _ in sub], [lab["authored_by"] for _, lab, _ in sub], fam)
        if r:
            print(f"  {fam:8s} AUC={r['auc']:.3f}  perm-p={r['p']:.3f}  classes={r['classes']}")

    # Target 2 — physics category as a positive control: the pipeline should find
    # this, because the text names the physics.
    cats = collections.Counter(src.get("category") for _, _, src in rows if src.get("category"))
    keep = {c for c, n in cats.items() if n >= 4}
    subc = [(it, lab, src) for it, lab, src in rows if src.get("category") in keep]
    print(f"\ntarget: physics category (control, n={len(subc)}, {len(keep)} categories)")
    for fam, fn in (("content", text_of), ("style", style_text), ("length", length_only)):
        r = evaluate([fn(it) for it, _, _ in subc], [src.get("category") for _, _, src in subc], fam)
        if r:
            print(f"  {fam:8s} AUC={r['auc']:.3f}  perm-p={r['p']:.3f}  classes={r['classes']}")

    # Structural check: are two dominant authors' texts separable by a trivial
    # length heuristic alone? If so, length normalisation is needed before scoring.
    print("\nlength only:")
    for a in top2:
        lens = [len(text_of(it).split()) for it, lab, _ in sub if lab["authored_by"] == a]
        print(f"  {a:34s} mean words={np.mean(lens):6.1f}  sd={np.std(lens):5.1f}  n={len(lens)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
