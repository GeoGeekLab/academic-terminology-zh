#!/usr/bin/env python3
"""Read-only terminology lookup over the bundled database and optional custom domains.

Python 3.10+ / standard library only. The original database archive is never modified.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

TERM_PATH = re.compile(r"(?:^|/)([a-z][a-z0-9_-]*)/indexes/terms\.csv$")
DOMAIN_ALIASES = {
    "marine": "oceanography", "ocean": "oceanography", "海洋": "oceanography", "海洋学": "oceanography",
    "ai": "artificial_intelligence", "ml": "artificial_intelligence", "machine-learning": "artificial_intelligence",
    "machine_learning": "artificial_intelligence", "机器学习": "artificial_intelligence", "人工智能": "artificial_intelligence",
    "remote": "remote_sensing", "rs": "remote_sensing", "遥感": "remote_sensing",
    "stats": "statistics", "stat": "statistics", "统计": "statistics", "统计学": "statistics",
}


def search_roots() -> list[Path]:
    seen: set[Path] = set()
    result = []
    for path in (Path.cwd(), Path(__file__).resolve().parent):
        for root in (path, *path.parents):
            if root not in seen:
                result.append(root)
                seen.add(root)
    return result


def resolve_db(explicit: str | None) -> Path:
    if explicit:
        candidates = [Path(explicit).expanduser()]
    elif os.getenv("GB_TERMINOLOGY_DB_ROOT"):
        candidates = [Path(os.environ["GB_TERMINOLOGY_DB_ROOT"]).expanduser()]
    else:
        candidates = [candidate for root in search_roots() for candidate in (
            root / "data/gb_terminology_databases.zip",
            root / "gb_terminology_databases.zip",
            root / "gb_terminology_databases",
            root / "data/gb_terminology_databases",
        )]
    for path in candidates:
        if path.is_file() and zipfile.is_zipfile(path):
            return path.resolve()
        if path.is_dir() and any(path.glob("*/indexes/terms.csv")):
            return path.resolve()
    raise FileNotFoundError("未找到术语库。请检查 data/gb_terminology_databases.zip 或使用 --db 指定路径。")


def normalized(text: str) -> str:
    return unicodedata.normalize("NFKC", str(text or "")).casefold().strip()


def parse_csv(contents: str, domain: str) -> list[dict]:
    return [{"domain": domain, **row} for row in csv.DictReader(io.StringIO(contents))]


def load_database(db: Path) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = {}
    if db.is_file():
        with zipfile.ZipFile(db) as archive:
            for name in sorted(archive.namelist()):
                match = TERM_PATH.search(name)
                if match:
                    domain = match.group(1)
                    content = archive.read(name).decode("utf-8-sig")
                    result.setdefault(domain, []).extend(parse_csv(content, domain))
    else:
        for path in sorted(db.glob("*/indexes/terms.csv")):
            domain = path.parent.parent.name
            result.setdefault(domain, []).extend(parse_csv(path.read_text(encoding="utf-8-sig"), domain))
    return result


def load_custom(db: Path) -> dict[str, list[dict]]:
    roots = [r / "custom_terms" for r in search_roots()]
    roots += [db.parent / "custom_terms", db.parent.parent / "custom_terms"]
    found: dict[str, list[dict]] = {}
    seen: set[Path] = set()
    for root in roots:
        root = root.resolve()
        if root in seen or not root.is_dir():
            continue
        seen.add(root)
        for path in sorted(root.glob("*/indexes/terms.csv")):
            domain = path.parent.parent.name
            if re.fullmatch(r"[a-z][a-z0-9_-]*", domain):
                found.setdefault(domain, []).extend(parse_csv(path.read_text(encoding="utf-8-sig"), domain))
    return found


def row_identity(row: dict) -> tuple[str, str, str, str, str]:
    return tuple(normalized(row.get(k, "")) for k in ("domain", "standard", "clause", "zh", "en"))


def load_all(db: Path) -> dict[str, list[dict]]:
    base = load_database(db)
    seen = {row_identity(row) for records in base.values() for row in records}
    for domain, records in load_custom(db).items():
        for row in records:
            identity = row_identity(row)
            if identity not in seen:
                base.setdefault(domain, []).append(row)
                seen.add(identity)
    return base


def aliases(text: str) -> list[str]:
    return [normalized(part) for part in re.split(r"[;,；、|]", text or "") if part.strip()]


def score(row: dict, query: str, include_definition: bool) -> int:
    q = normalized(query)
    if not q:
        return 0
    main = [normalized(row.get(k, "")) for k in ("zh", "en", "abbr")]
    secondary = aliases(row.get("aliases_zh", "")) + aliases(row.get("aliases_en", ""))
    if q in main:
        return 100
    if q in secondary:
        return 95
    values = [x for x in main + secondary if x]
    if any(x.startswith(q) for x in values):
        return 65
    if q.isascii() and q.isalpha():
        pattern = re.compile(r"(?<![a-z])" + re.escape(q) + r"(?![a-z])")
        if any(pattern.search(x) for x in values):
            return 55
    elif any(q in x for x in values):
        return 55
    return 20 if include_definition and q in normalized(row.get("definition", "")) else 0


def matches(rows: list[dict], query: str, limit: int, in_definition: bool) -> list[dict]:
    ranked = [(score(row, query, in_definition), row) for row in rows]
    ranked = [(s, row) for s, row in ranked if s]
    ranked.sort(key=lambda sr: (-sr[0], sr[1].get("domain", ""), sr[1].get("zh", "")))
    return [dict(row, match_score=s) for s, row in ranked[:limit]]


def summarize(row: dict, detail: bool) -> dict:
    keys = ("id", "domain", "zh", "en", "abbr", "aliases_zh", "aliases_en", "standard", "clause", "physical_pdf_pages", "source_url", "match_score")
    if detail:
        keys += ("definition", "notes", "symbol", "review_scope", "verification")
    return {key: row.get(key, "") for key in keys}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="查询术语库和扩展领域（只读）")
    p.add_argument("--db", help="数据库 ZIP 或解压目录；亦可设置 GB_TERMINOLOGY_DB_ROOT")
    p.add_argument("--q", action="append", default=[], help="要检索的中文或英文术语；可重复")
    p.add_argument("--domain", action="append", default=[], help="领域名称或别名；不指定则跨领域")
    p.add_argument("--limit", type=int, default=5, help="每个查询最多结果数，1–20")
    p.add_argument("--detail", action="store_true", help="返回定义、注释、核验状态")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    p.add_argument("--in-definition", action="store_true", help="额外匹配定义正文")
    p.add_argument("--stats", action="store_true", help="显示全部可用领域和术语数量")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if not (args.q or args.stats) or not 1 <= args.limit <= 20:
        print("请指定 --q 或 --stats，且 --limit 须在 1–20 之间", file=sys.stderr)
        return 2
    try:
        db = resolve_db(args.db)
        all_rows = load_all(db)
    except (OSError, ValueError, KeyError, UnicodeError, zipfile.BadZipFile) as exc:
        print(f"术语库读取失败：{exc}", file=sys.stderr)
        return 2
    domain_names = []
    for raw in args.domain:
        key = normalized(raw)
        name = key if key in all_rows else DOMAIN_ALIASES.get(key, key)
        if name not in all_rows:
            print(f"未知领域：{raw}；可用领域：{', '.join(sorted(all_rows))}", file=sys.stderr)
            return 2
        if name not in domain_names:
            domain_names.append(name)
    selected = domain_names or sorted(all_rows)
    if args.stats:
        counts = {domain: len(all_rows[domain]) for domain in (selected if args.domain else sorted(all_rows))}
        if args.json and not args.q:
            print(json.dumps({"database": str(db), "counts": counts}, ensure_ascii=False, indent=2))
        elif not args.json:
            print("\n".join(f"{domain}: {count}" for domain, count in counts.items()))
        if not args.q:
            return 0
    rows = [r for domain in selected for r in all_rows[domain]]
    results = {q: [summarize(r, args.detail) for r in matches(rows, q, args.limit, args.in_definition)] for q in args.q}
    if args.json:
        print(json.dumps({"database": str(db), "results": results}, ensure_ascii=False, indent=2))
    else:
        for q, candidates in results.items():
            print(f"\n【{q}】{len(candidates)} 条候选")
            for r in candidates:
                print(f"- [{r['domain']}] {r['zh']} / {r['en']} | {r['standard']} §{r['clause']} | PDF p.{r['physical_pdf_pages']}")
                if args.detail:
                    if r.get("aliases_zh") or r.get("aliases_en"):
                        print(f"  别名：{r.get('aliases_zh', '')} | {r.get('aliases_en', '')}")
                    print(f"  定义：{r.get('definition', '')}")
                    if r.get("notes"):
                        print(f"  注释：{r['notes']}")
                    print(f"  核验：{r.get('review_scope', '')} ({r.get('verification', '')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
