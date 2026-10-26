#!/usr/bin/env python3
"""Verify standards-source inventory; optionally gate releases on documented clearance."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/rights_manifest.json"
INDEX_ROOT = ROOT / "data/gb_terminology_databases"


def audit(manifest_path: Path = MANIFEST, index_root: Path = INDEX_ROOT) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {}
    for source in manifest["sources"]:
        key = (source["domain"], source["standard"])
        if key in expected:
            raise ValueError(f"duplicate manifest standard {key}")
        expected[key] = source
    actual = Counter()
    for csv_file in sorted(index_root.glob("*/indexes/terms.csv")):
        with csv_file.open(encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                standard = row.get("standard", "").strip()
                if not standard or not row.get("zh", "").strip() or not row.get("clause", "").strip():
                    raise ValueError(f"required provenance field missing in {csv_file}")
                actual[(csv_file.parent.parent.name, standard)] += 1
    if not actual:
        raise ValueError("no terms found")
    if set(expected) != set(actual):
        raise ValueError(f"source mismatch: missing={sorted(set(actual)-set(expected))}, "
                         f"unexpected={sorted(set(expected)-set(actual))}")
    for key, count in actual.items():
        if expected[key].get("records") != count:
            raise ValueError(f"{key}: expected {expected[key].get('records')}, found {count}")
    cleared = []
    uncleared = []
    for key, entry in expected.items():
        if (entry.get("redistribution_status") == "cleared"
                and entry.get("rights_holder_verified") is True
                and entry.get("counsel_reviewed") is True
                and isinstance(entry.get("permission_document_url"), str)
                and entry["permission_document_url"].startswith("https://")):
            cleared.append(key[1])
        else:
            uncleared.append(key[1])
    return {"index_records": sum(actual.values()), "standard_count": len(actual),
            "cleared": sorted(cleared), "uncleared": sorted(uncleared),
            "release_ready": len(uncleared) == 0,
            "warning": "A manifest entry is a documentary checkpoint, not a legal determination."}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--require-clearance", action="store_true",
                   help="Fail a public source release while any standards have no documented clearance")
    args = p.parse_args(argv)
    try:
        report = audit()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if args.require_clearance and not report["release_ready"]:
            print("release blocked: third-party data redistribution not cleared", file=sys.stderr)
            return 3
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"rights audit failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
