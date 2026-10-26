#!/usr/bin/env python3
"""Source-attributed, paired terminology benchmark. Stdlib only; no model calls."""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

DEFAULT_CASES = Path(__file__).with_name("real_papers.jsonl")


def read_jsonl(path: Path) -> list[dict]:
    result = []
    with path.open(encoding="utf-8") as stream:
        for number, raw in enumerate(stream, 1):
            if not raw.strip():
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{number}: invalid JSON: {exc}") from exc
            if not isinstance(item, dict):
                raise ValueError(f"{path}:{number}: expected a JSON object")
            result.append(item)
    if not result:
        raise ValueError(f"{path}: no records")
    return result


def validate_cases(cases: list[dict]) -> None:
    seen = set()
    for case in cases:
        cid = case.get("id")
        if not isinstance(cid, str) or not cid or cid in seen:
            raise ValueError(f"missing or duplicate case id: {cid!r}")
        seen.add(cid)
        for field in ("authors", "modifications", "source_title", "source_url", "doi", "excerpt", "prompt", "license_url"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise ValueError(f"{cid}: missing {field}")
        if not case["source_url"].startswith("https://"):
            raise ValueError(f"{cid}: source must use HTTPS")
        if case.get("license") != "CC BY 4.0" or case["license_url"] != "https://creativecommons.org/licenses/by/4.0/":
            raise ValueError(f"{cid}: license needs individual source review")
        allowed_tasks = {
            "terminology_audit_zh", "methodology_integrity_zh",
            "mechanism_consistency_zh", "statistical_scope_zh",
            "document_consistency_zh", "metric_integrity_zh",
        }
        if case.get("task") not in allowed_tasks:
            raise ValueError(f"{cid}: unsupported task")
        if case.get("case_type") != "paper_grounded_synthetic_challenge":
            raise ValueError(f"{cid}: the scenario must be explicitly identified as constructed")
        if not isinstance(case.get("input_text"), str) or not case["input_text"].strip():
            raise ValueError(f"{cid}: missing constructed input_text")
        if not isinstance(case.get("expected_checks"), list) or not case["expected_checks"] or not all(
            isinstance(check, str) and check.strip() for check in case["expected_checks"]
        ):
            raise ValueError(f"{cid}: expected_checks must be nonempty")
        if case.get("human_review_required") is not True:
            raise ValueError(f"{cid}: human review is required")
        if not isinstance(case.get("gold_reviewed"), bool):
            raise ValueError(f"{cid}: explicit gold_reviewed is required")
        concepts = case.get("concepts")
        if not isinstance(concepts, list) or not concepts:
            raise ValueError(f"{cid}: concepts must be nonempty")
        concept_ids = set()
        for concept in concepts:
            if not isinstance(concept, dict) or not isinstance(concept.get("id"), str):
                raise ValueError(f"{cid}: invalid concept")
            if concept["id"] in concept_ids:
                raise ValueError(f"{cid}: duplicate concept: {concept['id']}")
            concept_ids.add(concept["id"])
            accepted = concept.get("accepted")
            if not isinstance(accepted, list) or not accepted or not all(isinstance(t, str) and t.strip() for t in accepted):
                raise ValueError(f"{cid}: invalid accepted terminology")
            if not isinstance(concept.get("in_index"), bool):
                raise ValueError(f"{cid}: in_index must be a boolean")
        literals = case.get("protected_literals")
        if not isinstance(literals, list) or not all(isinstance(x, str) and x for x in literals):
            raise ValueError(f"{cid}: protected_literals must be strings")


def normalize(value: str) -> str:
    return "".join(unicodedata.normalize("NFKC", value).casefold().split())


def score_one(case: dict, response: str) -> dict:
    normalized = normalize(response)
    concepts = {
        term["id"]: any(normalize(accepted) in normalized for accepted in term["accepted"])
        for term in case["concepts"]
    }
    protected = {literal: normalize(literal) in normalized for literal in case["protected_literals"]}
    return {"concepts": concepts, "protected": protected,
            "concept_hits": sum(concepts.values()), "concept_total": len(concepts),
            "protected_hits": sum(protected.values()), "protected_total": len(protected)}


def load_pairs(cases: list[dict], path: Path) -> list[dict]:
    rows = read_jsonl(path)
    expected = {c["id"] for c in cases}
    seen = set()
    for row in rows:
        cid = row.get("id")
        if not isinstance(cid, str) or cid in seen or cid not in expected:
            raise ValueError(f"unexpected or duplicate output id: {cid!r}")
        seen.add(cid)
        for arm in ("baseline", "skill"):
            if not isinstance(row.get(arm), str) or not row[arm].strip():
                raise ValueError(f"{cid}: {arm} output is empty")
    if seen != expected:
        raise ValueError(f"missing outputs for: {', '.join(sorted(expected - seen))}")
    return rows


def compare(cases: list[dict], paired_outputs: list[dict]) -> dict:
    by_id = {item["id"]: item for item in paired_outputs}
    counts = {arm: {"concept_hits": 0, "concept_total": 0,
                    "protected_hits": 0, "protected_total": 0}
              for arm in ("baseline", "skill")}
    details = []
    for case in cases:
        output = by_id[case["id"]]
        result = {"id": case["id"], "task": case["task"], "gold_reviewed": case["gold_reviewed"],
                  "human_review_required": True, "expert_checks": case["expected_checks"]}
        for arm in ("baseline", "skill"):
            outcome = score_one(case, output[arm])
            result[arm] = outcome
            for field in counts[arm]:
                counts[arm][field] += outcome[field]
        details.append(result)

    def percent(numerator: int, denominator: int) -> float | None:
        return round(100 * numerator / denominator, 2) if denominator else None

    for arm in counts:
        item = counts[arm]
        item["concept_coverage_pct"] = percent(item["concept_hits"], item["concept_total"])
        item["protected_literal_recall_pct"] = percent(item["protected_hits"], item["protected_total"])

    base = counts["baseline"]["concept_coverage_pct"]
    skill = counts["skill"]["concept_coverage_pct"]
    return {
        "case_count": len(cases),
        "gold_reviewed_count": sum(c["gold_reviewed"] for c in cases),
        "benchmark_type": "paper-grounded constructed Chinese review tasks, not verbatim paper flaws",
        "metrics": counts,
        "skill_minus_baseline_concept_pp": round(skill - base, 2) if base is not None and skill is not None else None,
        "per_case": details,
        "limitations": [
            "These scores measure annotated phrase coverage and literal retention, not semantic correctness.",
            "Human assessment of expected_checks is the primary endpoint for these six difficult tasks.",
            "Constructed input_text is not quoted from, or alleged to be an error in, its linked paper.",
            "Substring matching can yield false positives, and accepted variants require expert review.",
            "The gold_reviewed flag must be true before results can support scientific quality claims.",
            "Use the same model, prompt policy and decoding settings for both arms; blind-review factual accuracy.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "template", "compare"):
        command = sub.add_parser(name)
        command.add_argument("--cases", type=Path, default=DEFAULT_CASES)
        if name == "template":
            command.add_argument("--out", type=Path, required=True)
        if name == "compare":
            command.add_argument("--outputs", type=Path, required=True)
            command.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        cases = read_jsonl(args.cases)
        validate_cases(cases)
        if args.command == "validate":
            print(json.dumps({"valid": True, "cases": len(cases),
                              "gold_reviewed": sum(c["gold_reviewed"] for c in cases)}, ensure_ascii=False))
        elif args.command == "template":
            if args.out.exists():
                raise ValueError(f"refusing to overwrite: {args.out}")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open("w", encoding="utf-8") as file:
                for case in cases:
                    file.write(json.dumps({
                        "id": case["id"],
                        "task": case["task"],
                        "task_prompt": case["prompt"] + "\n\n" + case["input_text"],
                        "baseline": "", "skill": ""
                    }, ensure_ascii=False) + "\n")
            print(f"wrote paired input template: {args.out}")
        else:
            report = compare(cases, load_pairs(cases, args.outputs))
            data = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
            if args.out:
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text(data, encoding="utf-8")
            else:
                print(data, end="")
        return 0
    except (OSError, ValueError) as exc:
        print(f"benchmark error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
