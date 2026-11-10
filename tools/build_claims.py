#!/usr/bin/env python3
"""Turn the pinned morphism snapshot into an explicit claims register.

Each morphism becomes one claim with a stated falsification condition. Nothing
here is invented: statements are restatements of the record's own fields, and
any field the record left vague stays vague. Vagueness is preserved rather than
smoothed, because an evaluator needs to see where the record is thin.

Usage:
    python3 tools/build_claims.py --snapshot snapshot --out claims
"""

import argparse
import json
from collections import Counter
import pathlib

VERB = {
    "proved": "is established",
    "conjectured": "is proposed but not established",
    "partial": "is partially established",
}


def parse_extracted(raw):
    """citations_extracted is a JSON array string parsed from the prose note."""
    if not raw:
        return []
    try:
        val = json.loads(raw)
        return val if isinstance(val, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def classify_evidence(raw, extracted=None):
    """The `evidence` column is TEXT but holds two incompatible things.

    Some records store a JSON-serialised list of citations; others store a
    free-text experiment note. A few store the literal string "test morphism".
    Return (kind, citations) so the register does not present a note as a citation.

    When a prose note has author-year references parsed out of it, those are
    reported as a distinct kind so nobody mistakes a regex extraction for a
    curated citation list.
    """
    if raw is None or raw == "":
        return ("citation_in_prose", extracted) if extracted else ("absent", [])
    if isinstance(raw, list):
        return "citation_list", raw
    text = str(raw).strip()
    if text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return "citation_list", parsed
        except json.JSONDecodeError:
            return "unparseable_json", []
    if "test morphism" in text.lower():
        return "test_placeholder", []
    if extracted:
        return "citation_in_prose", extracted
    return "experiment_note", [text]


def structural_defects(m, kind):
    """Record what is missing, rather than letting an evaluator infer it."""
    out = []
    if not m.get("transfer_operator"):
        out.append("no transfer_operator: the record names no mechanism, so no result can cross")
    if not m.get("breakdown_boundary"):
        out.append("no breakdown_boundary: the record does not say where the correspondence fails")
    if not m.get("math_invariant"):
        out.append("no math_invariant: the claim has no mathematical content")
    if not m.get("physics_invariant"):
        out.append("no physics_invariant: the claim has no physical content")
    if kind == "test_placeholder":
        out.append("placeholder record: evidence is 'test morphism'; this is test data in the corpus")
    return out


def falsification(m):
    """State what would show this claim false, using only the record's fields."""
    parts = [
        f"The record asserts that {m.get('math_invariant', '(no math invariant stated)')} "
        f"corresponds to {m.get('physics_invariant', '(no physics invariant stated)')}."
    ]
    if m.get("transfer_operator"):
        parts.append(
            "It is refuted if that transfer does not act on the objects named, or if no "
            "result can cross between the two sides using it."
        )
    else:
        parts.append(
            "It is refuted if no transfer operator can be supplied, since a correspondence "
            "without one carries no result."
        )
    if m.get("breakdown_boundary"):
        parts.append(f"The record's own stated limit: {m['breakdown_boundary']}")
    else:
        parts.append("The record states no breakdown boundary, which is itself a weakness.")
    return " ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default="snapshot")
    ap.add_argument("--out", default="claims")
    args = ap.parse_args()

    snap = pathlib.Path(args.snapshot)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    morphisms = json.loads((snap / "morphisms.json").read_text())["flat"]
    claims = []
    for m in sorted(morphisms, key=lambda x: (str(x.get("math_id")), str(x.get("physics_id")), str(x.get("id")))):
        mid = str(m.get("math_id"))
        kind, cites = classify_evidence(
            m.get("evidence"), parse_extracted(m.get("citations_extracted"))
        )
        claims.append({
            "claim_id": f"E{m.get('math_id')}->{m.get('physics_id')}",
            "source_record_id": m.get("id"),
            "math_id": mid,
            "physics_id": m.get("physics_id"),
            "asserted_strength": m.get("strength"),
            "strength_reading": VERB.get(str(m.get("strength")).lower(), "has unstated status"),
            "claim": (
                f"{m.get('math_object', '(unnamed math object)')} "
                f"[{m.get('math_invariant', 'no invariant stated')}] "
                f"corresponds to {m.get('physics_name') or m.get('physics_id')} "
                f"[{m.get('physics_invariant', 'no invariant stated')}]"
            ),
            "transfer_operator_claimed": m.get("transfer_operator"),
            "breakdown_boundary": m.get("breakdown_boundary"),
            "falsification_condition": falsification(m),
            "evidence_kind": kind,
            "evidence_raw": m.get("evidence"),
            "citations": cites,
            "citations_verified": False,
            "structural_defects": structural_defects(m, kind),
            "anchor": f"https://www.erdosproblems.com/{mid}",
            "recorded_by": m.get("created_by"),
            "recorded_date": m.get("created_date"),
            "evaluation": {"verdict": None, "axes": None, "note": None},
        })

    register = {
        "generated_from": str(snap / "morphisms.json"),
        "claim_count": len(claims),
        "evidence_kind_counts": dict(Counter(c["evidence_kind"] for c in claims)),
        "structural_defect_counts": dict(
            Counter(d.split(":")[0] for c in claims for d in c["structural_defects"])
        ),
        "claims_with_structural_defects": sum(1 for c in claims if c["structural_defects"]),
        "generation_note": (
            "Statements are mechanical restatements of each morphism record's own fields. "
            "citations_verified is false for every claim at generation time; verifying them "
            "is part of the evaluation, not a precondition."
        ),
        "claims": claims,
    }
    (out / "CLAIMS_REGISTER.json").write_text(
        json.dumps(register, indent=2, ensure_ascii=False) + "\n"
    )

    lines = [
        "# Claims register",
        "",
        f"{len(claims)} claims, generated mechanically from `snapshot/morphisms.json`.",
        "Every field below is quoted from the morphism record; nothing was inferred.",
        "",
        "| Claim | Strength | Math side | Physics side |",
        "|---|---|---|---|",
    ]
    for c in claims:
        lines.append(
            f"| `{c['claim_id']}` | {c['asserted_strength']} | "
            f"{c['claim'].split(' [')[0]} | {c['physics_id']} |"
        )
    lines += [
        "",
        "## How to read `asserted_strength`",
        "",
        "`proved` in a record means the atlas asserts the correspondence is established.",
        "It does not automatically mean the *underlying classical theorem* is what was",
        "proved. Separating those two readings is the single highest-value check in this",
        "evaluation.",
        "",
    ]
    (out / "CLAIMS_REGISTER.md").write_text("\n".join(lines))
    print(f"wrote {len(claims)} claims to {out}/")


if __name__ == "__main__":
    main()
