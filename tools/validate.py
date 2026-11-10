#!/usr/bin/env python3
"""Confirm the local snapshot matches the pinned manifest.

Run this before evaluating anything. If it fails, you are not looking at the
target the manifest describes, and findings will not be reproducible.

Exit codes: 0 all good, 1 hash mismatch, 2 structural problem.
"""

import hashlib
import json
import pathlib
import sys


def main(root="."):
    base = pathlib.Path(root)
    man_path = base / "snapshot" / "manifest.json"
    if not man_path.exists():
        print(f"FAIL: missing {man_path}")
        return 2

    man = json.loads(man_path.read_text())
    expected = man.get("sha256", {})
    problems = []

    for name, want in sorted(expected.items()):
        p = base / "snapshot" / name
        if not p.exists():
            problems.append(f"missing payload: {name}")
            continue
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        if got != want:
            problems.append(f"hash mismatch: {name}\n  want {want}\n  got  {got}")

    rec = man.get("reconciliation", {})
    declares = [rec.get("morphisms_declared"), rec.get("physics_declared")]
    captured = [rec.get("morphisms_captured"), rec.get("physics_captured")]
    for label, d, c in zip(("morphisms", "physics"), declares, captured):
        if d is None or c is None:
            problems.append(f"manifest lacks {label} reconciliation")
        elif c < d:
            print(f"NOTE: {label}: captured {c} of {d} declared "
                  f"({100 * c / d:.0f}% coverage) — see KNOWN_ISSUES.md")

    reg = base / "claims" / "CLAIMS_REGISTER.json"
    if reg.exists():
        n = json.loads(reg.read_text()).get("claim_count")
        if n != rec.get("morphisms_captured"):
            problems.append(
                f"claims register has {n} claims but snapshot captured "
                f"{rec.get('morphisms_captured')} morphisms — rebuild the register"
            )
    else:
        print("NOTE: claims/CLAIMS_REGISTER.json absent; run tools/build_claims.py")

    if problems:
        print("FAIL")
        for p in problems:
            print(" -", p)
        return 1

    print("OK: snapshot matches manifest")
    print(f"    captured {man['captured']}")
    print(f"    pinned at {man['snapshot_utc']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
