import csv
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
LOOKUP = BASE / "scripts/lookup.py"
IMPORT = BASE / "scripts/import_terms.py"


class TestExtensions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root / "gb_terminology_databases.zip"
        csv_file = self.root / "statistics.csv"
        with csv_file.open("w", encoding="utf8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["zh", "en", "standard", "clause"])
            w.writeheader()
            w.writerow({"zh": "回归分析", "en": "regression analysis", "standard": "GB/T demo", "clause": "1.1"})
        with zipfile.ZipFile(self.db, "w") as z:
            z.write(csv_file, "statistics/indexes/terms.csv")
        self.csv_file = self.root / "to_import.csv"
        with self.csv_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["zh", "en", "definition", "clause"])
            writer.writeheader()
            writer.writerow({"zh": "净初级生产力", "en": "net primary productivity", "definition": "净初级生产过程产生的有机物量", "clause": "2.1"})

    def tearDown(self):
        self.tmp.cleanup()

    def run_lookup(self, *args):
        return subprocess.run([sys.executable, str(LOOKUP), "--db", str(self.db), *args], cwd=self.root, capture_output=True, text=True)

    def import_data(self, *extra):
        return subprocess.run([sys.executable, str(IMPORT), "--domain", "ecology", "--input", str(self.csv_file), "--source", "某学术词表", *extra], cwd=self.root, capture_output=True, text=True)

    def test_import_and_discover(self):
        outcome = self.import_data()
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        self.assertEqual(json.loads(outcome.stdout)["new"], 1)
        count = self.run_lookup("--stats", "--json")
        self.assertEqual(json.loads(count.stdout)["counts"], {"ecology": 1, "statistics": 1})
        hit = self.run_lookup("--q", "净初级生产力", "--domain", "ecology", "--detail", "--json")
        self.assertEqual(hit.returncode, 0, hit.stderr)
        rows = json.loads(hit.stdout)["results"]["净初级生产力"]
        self.assertEqual(rows[0]["standard"], "某学术词表")
        self.assertEqual(rows[0]["verification"], "imported_unverified")

    def test_reimport_is_idempotent(self):
        self.assertEqual(self.import_data().returncode, 0)
        outcome = self.import_data()
        self.assertEqual(json.loads(outcome.stdout)["new"], 0)
        self.assertEqual(json.loads(outcome.stdout)["total"], 1)

    def test_import_jsonl(self):
        path = self.root / "glossary.jsonl"
        path.write_text(json.dumps({"zh": "海雾", "en": "sea fog", "standard": "Test glossary", "clause": "1"}, ensure_ascii=False) + "\n", encoding="utf8")
        outcome = subprocess.run([sys.executable, str(IMPORT), "--domain", "climate_science", "--input", str(path)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        rows = json.loads(self.run_lookup("--q", "海雾", "--domain", "climate_science", "--json").stdout)["results"]["海雾"]
        self.assertEqual(rows[0]["en"], "sea fog")

    def test_unrecognized_domain_rejected(self):
        self.assertEqual(self.run_lookup("--domain", "does_not_exist", "--q", "anything").returncode, 2)

    def test_invalid_pdf_import_rejected(self):
        path = self.root / "dummy.pdf"
        path.write_bytes(b"%PDF-1.7")
        outcome = subprocess.run([sys.executable, str(IMPORT), "--domain", "ecology", "--input", str(path)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(outcome.returncode, 2)
        self.assertIn("PDF", outcome.stderr)


if __name__ == "__main__":
    unittest.main()
