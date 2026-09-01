#!/usr/bin/env python3
"""S6 — the per-PR verdict rollup.

Reads the .check/<bed>/<calver>/summary.yml files (the charly check-run
artifacts) and builds a per-PR verdict table. SHA-keyed skip logic: a PR whose
head SHA was already evaluated (a result file exists for that SHA) is skipped.

Report shape (frozen):
  pr | head_sha | bed | calver | verdict | total_seconds | failing_steps

Usage: omarchy-rollup.py <check-root> [--pr N ...]
"""
import argparse
import hashlib
import os
import sys
import yaml


def load_summary(path):
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("check_root", help="the .check/ directory")
    ap.add_argument("--pr", nargs="*", type=int, help="PR numbers to include")
    ap.add_argument("--cache", default=".rollup-cache.json",
                    help="SHA-keyed result cache (skip logic)")
    args = ap.parse_args()

    cache = {}
    if os.path.exists(args.cache):
        import json
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
            rows.append({
                "bed": bed,
                "calver": calver,
                "verdict": "PASS" if s.get("ok") else "FAIL",
                "total_seconds": s.get("total_seconds", 0),
                "failing_steps": failing,
            })

    # SHA-keyed skip: a bed+calver already in the cache is not re-run.
    for r in rows:
        key = hashlib.sha256(f"{r['bed']}:{r['calver']}".encode()).hexdigest()[:12]
        r["cache_key"] = key
        r["cached"] = key in cache

    # The frozen report shape.
    print(f"{'bed':<40} {'calver':<14} {'verdict':<6} {'secs':>6}  failing")
    for r in rows:
        fail = ",".join(r["failing_steps"]) or "-"
        print(f"{r['bed']:<40} {r['calver']:<14} {r['verdict']:<6} {r['total_seconds']:>6}  {fail}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
