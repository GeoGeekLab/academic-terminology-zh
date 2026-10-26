"""Unit tests use synthetic outputs only. They are not real model performance."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("benchmark.py")
SPEC = importlib.util.spec_from_file_location("term_benchmark", MODULE_PATH)
benchmark = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(benchmark)


def example_case(cid="paper-a"):
    return {
        "id": cid, "task": "translate_en_zh", "source_title": "paper", "source_url": "https://example.org/paper",
        "doi": "10.1/example", "excerpt": "Machine learning 10 km", "prompt": "Translate",
        "license": "CC BY 4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "concepts": [{"id": "ml", "accepted": ["机器学习"], "in_index": True}],
        "protected_literals": ["10", "km"], "gold_reviewed": False,
    }


class BenchmarkTests(unittest.TestCase):
    def test_real_cases_schema(self):
        rows = benchmark.read_jsonl(benchmark.DEFAULT_CASES)
        benchmark.validate_cases(rows)
        self.assertGreaterEqual(len(rows), 5)
        self.assertFalse(any(c["gold_reviewed"] for c in rows))

    def test_paired_coverage_and_retention(self):
        cases = [example_case()]
        rows = [{"id": "paper-a", "baseline": "机器学习 10", "skill": "机器学习 10 km"}]
        report = benchmark.compare(cases, rows)
        self.assertEqual(report["metrics"]["baseline"]["concept_coverage_pct"], 100)
        self.assertEqual(report["metrics"]["baseline"]["protected_literal_recall_pct"], 50)
        self.assertEqual(report["metrics"]["skill"]["protected_literal_recall_pct"], 100)
        self.assertEqual(report["skill_minus_baseline_concept_pp"], 0)
        self.assertEqual(report["gold_reviewed_count"], 0)

    def test_missing_output_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pair.jsonl"
            path.write_text(json.dumps({"id": "paper-a", "baseline": "ok", "skill": ""}) + "\n")
            with self.assertRaisesRegex(ValueError, "empty"):
                benchmark.load_pairs([example_case()], path)

    def test_duplicate_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            benchmark.validate_cases([example_case(), example_case()])

    def test_missing_case_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pair.jsonl"
            path.write_text(json.dumps({"id": "paper-a", "baseline": "ok", "skill": "ok"}) + "\n")
            with self.assertRaisesRegex(ValueError, "missing outputs"):
                benchmark.load_pairs([example_case(), example_case("paper-b")], path)


if __name__ == "__main__":
    unittest.main()
