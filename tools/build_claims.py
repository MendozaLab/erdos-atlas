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
import pathlib

VERB = {
    "proved": "is established",
    "conjectured": "is proposed but not established",
    "partial": "is partially established",
}


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
            "citations_as_given": m.get("evidence", []),
            "citations_verified": False,
            "anchor": f"https://www.erdosproblems.com/{mid}",
            "recorded_by": m.get("created_by"),
            "recorded_date": m.get("created_date"),
            "evaluation": {"verdict": None, "axes": None, "note": None},
        })

    register = {
        "generated_from": str(snap / "morphisms.json"),
        "claim_count": len(claims),
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
