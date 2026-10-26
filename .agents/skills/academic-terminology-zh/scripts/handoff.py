#!/usr/bin/env python3
"""Emit read-only, source-attributed terminology mentions for other writing agents."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import lookup


def mentions(text: str, db: Path, domains: list[str], limit: int) -> list[dict]:
    all_rows = lookup.load_all(db)
    selected = []
    for requested in domains:
        canonical = lookup.DOMAIN_ALIASES.get(lookup.normalized(requested), lookup.normalized(requested))
        if canonical not in all_rows:
            raise ValueError(f"unknown domain: {requested}")
        if canonical not in selected:
            selected.append(canonical)
    selected = selected or sorted(all_rows)
    normalized = lookup.normalized(text)
    results = []
    seen = set()
    for domain in selected:
        for row in all_rows[domain]:
            candidates = [(row.get("zh", ""), False)]
            candidates += [(alias.strip(), True) for alias in re.split(r"[,;；、|]", row.get("aliases_zh", "")) if alias.strip()]
            for candidate, is_alias in candidates:
                term = lookup.normalized(candidate)
                if len(term) < 2 or term not in normalized:
                    continue
                identity = (domain, row.get("standard"), row.get("clause"), row.get("zh"))
                if identity in seen:
                    break
                seen.add(identity)
                results.append({
                    "match": candidate,
                    "alias_match": is_alias,
                    "domain": domain, "zh": row.get("zh", ""), "en": row.get("en", ""),
                    "standard": row.get("standard", ""), "clause": row.get("clause", ""),
                    "physical_pdf_pages": row.get("physical_pdf_pages", ""),
                    "verification": row.get("verification", ""),
                })
                break
    return sorted(results, key=lambda record: (-len(record["match"]), record["domain"], record["zh"]))[:limit]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, help="Text file (UTF-8); otherwise read stdin")
    p.add_argument("--domain", action="append", default=[])
    p.add_argument("--db", help="External database path; honors GB_TERMINOLOGY_DB_ROOT")
    p.add_argument("--limit", type=int, default=30)
    args = p.parse_args(argv)
    if not 1 <= args.limit <= 200:
        p.error("limit must be between 1 and 200")
    try:
        text = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
        if not text.strip():
            raise ValueError("empty text input")
        db = lookup.resolve_db(args.db)
        hits = mentions(text, db, args.domain, args.limit)
        print(json.dumps({"count": len(hits), "mentions": hits, "warning":
              "Candidates only; independently check meaning, verification status and source rights."},
              ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"handoff error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
