import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("skill_installer", Path(__file__).with_name("install.py"))
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "source"
        self.project = self.root / "project"
        skill = self.src / ".agents/skills" / installer.NAME
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("test skill", encoding="utf-8")
        data = self.src / "data/gb_terminology_databases/oceanography/indexes"
        data.mkdir(parents=True)
        (data / "terms.csv").write_text("zh,en\n海雾,sea fog\n", encoding="utf-8")

    def test_claude_install_without_data(self):
        installer.install(self.src, self.project, "claude")
        skill = self.project / ".claude/skills" / installer.NAME / "SKILL.md"
        self.assertEqual(skill.read_text(), "test skill")
        self.assertFalse((self.project / "data").exists())

    def test_codex_install_with_data(self):
        installer.install(self.src, self.project, "codex", with_data=True)
        self.assertTrue((self.project / ".agents/skills" / installer.NAME / "SKILL.md").exists())
        self.assertTrue((self.project / "data/gb_terminology_databases/oceanography/indexes/terms.csv").exists())

    def test_dry_run_is_side_effect_free(self):
        installer.install(self.src, self.project, "opencode", with_data=True, dry_run=True)
        self.assertFalse(self.project.exists())

    def test_no_implicit_overwrite(self):
        installer.install(self.src, self.project, "claude")
        with self.assertRaises(FileExistsError):
            installer.install(self.src, self.project, "claude")
        installer.install(self.src, self.project, "claude", force=True)

    def test_source_equals_target_does_not_delete(self):
        installer.install(self.src, self.src, "codex", with_data=True, force=True)
        self.assertTrue((self.src / ".agents/skills" / installer.NAME / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
