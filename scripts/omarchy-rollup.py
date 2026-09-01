#!/usr/bin/env python3
"""S6 — the per-PR verdict rollup.

Reads the .check/<bed>/<calver>/summary.yml files (the charly check-run
artifacts) and builds a per-PR verdict table. SHA-keyed skip logic: a bed whose
result is already in the cache (keyed by bed+calver) is reported as CACHED and
not re-run by the caller.

Report shape (frozen):
  bed | calver | verdict | secs | cached | failing

Usage: omarchy-rollup.py <check-root> [--cache FILE]
"""
import argparse
import hashlib
import json
import os
import sys
import yaml


def load_summary(path):
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("check_root", help="the .check/ directory")
    ap.add_argument("--cache", default=".rollup-cache.json",
                    help="SHA-keyed result cache (skip logic)")
    args = ap.parse_args()

    cache = {}
    if os.path.exists(args.cache):
        with open(args.cache) as f:
            cache = json.load(f)

    rows = []
    for bed in sorted(os.listdir(args.check_root)):
        bed_dir = os.path.join(args.check_root, bed)
        if not os.path.isdir(bed_dir):
            continue
        for calver in sorted(os.listdir(bed_dir)):
            summary_path = os.path.join(bed_dir, calver, "summary.yml")
            if not os.path.exists(summary_path):
                continue
            s = load_summary(summary_path)
            failing = [st["name"] for st in s.get("steps", []) if not st.get("ok")]
            key = hashlib.sha256(f"{bed}:{calver}".encode()).hexdigest()[:12]
            rows.append({
                "bed": bed,
                "calver": calver,
                "verdict": "PASS" if s.get("ok") else "FAIL",
                "total_seconds": s.get("total_seconds", 0),
                "failing_steps": failing,
                "cache_key": key,
                "cached": key in cache,
            })

    # Persist the cache: every evaluated bed+calver is recorded, so a later run
    # reports it as CACHED (the skip logic — the caller does not re-run a cached
    # bed). The cache is keyed by bed+calver (the SHA of the pair).
    for r in rows:
        cache[r["cache_key"]] = {"bed": r["bed"], "calver": r["calver"], "verdict": r["verdict"]}
    with open(args.cache, "w") as f:
        json.dump(cache, f, indent=2)

    # The frozen report shape.
    print(f"{'bed':<40} {'calver':<14} {'verdict':<6} {'secs':>6}  {'cached':<7} failing")
    for r in rows:
        fail = ",".join(r["failing_steps"]) or "-"
        print(f"{r['bed']:<40} {r['calver']:<14} {r['verdict']:<6} {r['total_seconds']:>6}  {str(r['cached']):<7} {fail}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
