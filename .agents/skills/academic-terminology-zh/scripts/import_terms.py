#!/usr/bin/env python3
"""Import a reviewed CSV/JSONL glossary as a searchable custom domain. Stdlib only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

FIELDS = [
    "id", "standard", "clause", "zh", "en", "abbr", "aliases_zh", "aliases_en",
    "definition", "notes", "symbol", "physical_pdf_pages", "review_scope",
    "verification", "source_url",
]


def records_from(path: Path) -> list[dict]:
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    if path.suffix.lower() == ".jsonl":
        with path.open(encoding="utf-8-sig") as handle:
            records = [json.loads(line) for line in handle if line.strip()]
            if any(not isinstance(record, dict) for record in records):
                raise ValueError("JSONL 每行必须是一个对象")
            return records
    raise ValueError("输入只支持经过提取和核对的 .csv 或 .jsonl；PDF 应先转成术语表")


def key(row: dict) -> tuple[str, ...]:
    return tuple(str(row.get(k) or "").strip().casefold() for k in ("standard", "clause", "zh", "en"))


def normalize_record(row: dict, domain: str, source: str) -> dict:
    record = {field: str(row.get(field) or "").strip() for field in FIELDS}
    record["standard"] = record["standard"] or source
    if not (record["zh"] or record["en"]):
        raise ValueError("每条记录必须至少有中文术语 zh 或英文术语 en")
    if not record["standard"]:
        raise ValueError("请提供每条记录的 standard 来源字段或 --source 参数")
    if not record["id"]:
        raw = "\u241f".join((domain, record["standard"], record["clause"], record["zh"], record["en"]))
        record["id"] = "custom:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    record["verification"] = record["verification"] or "imported_unverified"
    return record


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="将已整理的 CSV/JSONL 导入 custom_terms/<domain>，原四库不变")
    p.add_argument("--domain", required=True, help="扩展领域英文 slug，例如 climate_science")
    p.add_argument("--input", required=True, help="结构化 CSV 或 JSONL 文件")
    p.add_argument("--source", default="", help="当输入缺少 standard 字段时填写来源名称")
    p.add_argument("--out", default="custom_terms", help="输出目录，默认 ./custom_terms")
    args = p.parse_args(argv)
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", args.domain):
        p.error("--domain 只能包含小写英文、数字、连字符和下划线，且必须以字母开头")
    try:
        items = records_from(Path(args.input))
        if not items:
            raise ValueError("输入术语表为空")
        target = Path(args.out) / args.domain / "indexes" / "terms.csv"
        existing = records_from(target) if target.is_file() else []
        normalized = [normalize_record(item, args.domain, args.source) for item in items]
        combined = [normalize_record(item, args.domain, args.source) for item in existing]
        keys = {key(record) for record in combined}
        added = 0
        for record in normalized:
            if key(record) not in keys:
                combined.append(record)
                keys.add(key(record))
                added += 1
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8-sig", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(combined)
        print(json.dumps({"domain": args.domain, "new": added, "total": len(combined), "output": str(target)}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"导入失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
