import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "lookup.py"
COLUMNS = ["id", "standard", "clause", "zh", "en", "abbr", "aliases_zh", "aliases_en", "definition", "physical_pdf_pages", "verification", "notes", "symbol", "review_scope"]


def csv_content(items):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=COLUMNS)
    writer.writeheader()
    for item in items:
        writer.writerow(item)
    return out.getvalue()


class TestLookup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        sample = {
            "oceanography": [dict(id="o:1", zh="散射系数", en="scattering coefficient", standard="GB/T 15920", clause="1", definition="海洋学定义", physical_pdf_pages="2")],
            "remote_sensing": [dict(id="r:1", zh="散射系数", en="scattering coefficient", standard="GB/T 36299", clause="2", definition="遥感定义", physical_pdf_pages="3")],
            "artificial_intelligence": [dict(id="a:1", zh="机器学习", en="machine learning", standard="GB/T 41867", clause="3", definition="人工智能术语", physical_pdf_pages="4")],
            "statistics": [dict(id="s:1", zh="频率", en="frequency", standard="GB/T 3358", clause="4", definition="统计学术语", physical_pdf_pages="5")],
        }
        for domain, items in sample.items():
            path = self.root / domain / "indexes/terms.csv"
            path.parent.mkdir(parents=True)
            path.write_text(csv_content(items), encoding="utf-8-sig")
        self.zip_path = self.root / "db.zip"
        with zipfile.ZipFile(self.zip_path, "w") as z:
            for path in self.root.glob("*/indexes/terms.csv"):
                z.write(path, path.relative_to(self.root))

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, *args, db=None):
        return subprocess.run([sys.executable, str(SCRIPT), "--db", str(db or self.root), *args], capture_output=True, text=True)

    def test_directory_and_zip_read(self):
        for db in [self.root, self.zip_path]:
            out = self.invoke("--stats", "--json", db=db)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(sum(json.loads(out.stdout)["counts"].values()), 4)

    def test_cross_domain_result_preserved(self):
        out = self.invoke("--q", "散射系数", "--json")
        self.assertEqual(out.returncode, 0, out.stderr)
        rows = json.loads(out.stdout)["results"]["散射系数"]
        self.assertEqual({r["domain"] for r in rows}, {"oceanography", "remote_sensing"})

    def test_domain_filter_and_alias(self):
        out = self.invoke("--q", "散射系数", "--domain", "遥感", "--json")
        rows = json.loads(out.stdout)["results"]["散射系数"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["domain"], "remote_sensing")

    def test_exact_en_and_ai_boundary(self):
        out = self.invoke("--q", "machine learning", "--q", "AI", "--json")
        rows = json.loads(out.stdout)["results"]
        self.assertEqual(len(rows["machine learning"]), 1)
        self.assertEqual(rows["AI"], [])

    def test_no_invented_results(self):
        out = self.invoke("--q", "完全不存在的术语XYZ", "--json")
        self.assertEqual(json.loads(out.stdout)["results"]["完全不存在的术语XYZ"], [])

    def test_detail_opt_in(self):
        lite = json.loads(self.invoke("--q", "频率", "--json").stdout)["results"]["频率"][0]
        full = json.loads(self.invoke("--q", "频率", "--json", "--detail").stdout)["results"]["频率"][0]
        self.assertNotIn("definition", lite)
        self.assertEqual(full["definition"], "统计学术语")

    def test_invalid_domain(self):
        out = self.invoke("--q", "频率", "--domain", "chemistry")
        self.assertEqual(out.returncode, 2)

    def test_invalid_path(self):
        out = self.invoke("--q", "频率", db=self.root / "missing.zip")
        self.assertEqual(out.returncode, 2)


if __name__ == "__main__":
    unittest.main()
