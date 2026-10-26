import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "handoff.py"


class TestHandoff(unittest.TestCase):
    def test_mentions_with_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            terms = root / "oceanography/indexes/terms.csv"
            terms.parent.mkdir(parents=True)
            with terms.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["zh", "en", "aliases_zh", "standard", "clause", "verification"])
                writer.writeheader()
                writer.writerow({"zh": "水团", "en": "water mass", "aliases_zh": "水体", "standard": "GB/T test", "clause": "3.1", "verification": "unreviewed"})
            output = subprocess.run([sys.executable, str(SCRIPT), "--db", str(root), "--domain", "海洋"],
                                    input="研究水体结构与水团变化。", capture_output=True, text=True)
            self.assertEqual(output.returncode, 0, output.stderr)
            data = json.loads(output.stdout)
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["mentions"][0]["zh"], "水团")
            self.assertEqual(data["mentions"][0]["clause"], "3.1")
            self.assertEqual(data["mentions"][0]["verification"], "unreviewed")

    def test_unknown_domain_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            terms = root / "oceanography/indexes/terms.csv"
            terms.parent.mkdir(parents=True)
            terms.write_text("zh,en\n海雾,sea fog\n", encoding="utf-8")
            output = subprocess.run([sys.executable, str(SCRIPT), "--db", str(root), "--domain", "physics"],
                                    input="海雾", capture_output=True, text=True)
            self.assertEqual(output.returncode, 2)


if __name__ == "__main__":
    unittest.main()
