from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest
import importlib.util


ROOT = Path(__file__).resolve().parents[1]


class RepoCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "walnut.cli", *args, "--plain"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def run_cli_rich(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "walnut.cli", *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def test_topics_lists_all_roadmap_topics(self):
        result = self.run_cli("topics")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Arrays & Hashing", result.stdout)
        self.assertIn("Bit Manipulation", result.stdout)
        self.assertIn("18 topics", result.stdout)

    @unittest.skipUnless(importlib.util.find_spec("rich"), "rich is not installed")
    def test_topics_uses_rich_table_by_default(self):
        result = self.run_cli_rich("topics")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Walnut Roadmap", result.stdout)
        self.assertIn("┏", result.stdout)
        self.assertIn("Progress", result.stdout)

    @unittest.skipUnless(importlib.util.find_spec("rich"), "rich is not installed")
    def test_show_uses_rich_problem_panel_by_default(self):
        result = self.run_cli_rich("show", "3")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Two Sum", result.stdout)
        self.assertIn("Examples", result.stdout)
        self.assertIn("Try next", result.stdout)
        self.assertIn("╭", result.stdout)

    def test_show_works_for_unseeded_problem(self):
        result = self.run_cli("show", "15")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Best Time to Buy and Sell Stock", result.stdout)
        self.assertIn("https://leetcode.com/problems/best-time-to-buy-and-sell-stock/", result.stdout)

    def test_verify_all_seeded_references(self):
        result = self.run_cli("verify", "--all")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("14/14 seeded problems verified", result.stdout)

    def test_open_official_can_print_links_without_launching_browser(self):
        result = self.run_cli("open-official", "3", "--site", "leetcode", "--print")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("https://leetcode.com/problems/two-sum/", result.stdout)

    def test_notes_creates_ignored_local_notes_file(self):
        notes_path = ROOT / "problems/01-arrays-and-hashing/03-two-sum/notes.md"
        if notes_path.exists():
            notes_path.unlink()
        result = self.run_cli("notes", "3")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(notes_path.exists())
        self.assertIn("Two Sum", notes_path.read_text())
        notes_path.unlink()


if __name__ == "__main__":
    unittest.main()
