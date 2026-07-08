from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class ProgressTests(unittest.TestCase):
    def test_first_pass_sets_attempts_first_try_and_streak(self):
        from walnut.progress import default_progress, record_test_result

        progress = default_progress()
        record_test_result(
            progress,
            slug="two-sum",
            passed=False,
            cases_passed=2,
            cases_total=3,
            now=1_788_200_000,
            local_date="2026-07-01",
            time_sec=None,
            target_sec=900,
            revealed_hints=0,
            revealed_solution=False,
            slowest_case_sec=0.1,
        )
        record_test_result(
            progress,
            slug="two-sum",
            passed=True,
            cases_passed=3,
            cases_total=3,
            now=1_788_200_100,
            local_date="2026-07-01",
            time_sec=120,
            target_sec=900,
            revealed_hints=0,
            revealed_solution=False,
            slowest_case_sec=0.2,
        )

        problem = progress["problems"]["two-sum"]
        self.assertEqual(problem["status"], "solved")
        self.assertEqual(problem["test_runs"], 2)
        self.assertEqual(problem["attempts"], 2)
        self.assertFalse(problem["first_try"])
        self.assertEqual(problem["best_time_sec"], 120)
        self.assertEqual(progress["streak"]["current"], 1)

    def test_run_after_solve_does_not_change_attempts_or_first_try(self):
        from walnut.progress import default_progress, record_test_result

        progress = default_progress()
        record_test_result(
            progress,
            slug="contains-duplicate",
            passed=True,
            cases_passed=4,
            cases_total=4,
            now=1_788_200_000,
            local_date="2026-07-01",
            time_sec=60,
            target_sec=900,
            revealed_hints=0,
            revealed_solution=False,
            slowest_case_sec=0.1,
        )
        record_test_result(
            progress,
            slug="contains-duplicate",
            passed=True,
            cases_passed=4,
            cases_total=4,
            now=1_788_286_400,
            local_date="2026-07-02",
            time_sec=30,
            target_sec=900,
            revealed_hints=0,
            revealed_solution=False,
            slowest_case_sec=0.1,
        )

        problem = progress["problems"]["contains-duplicate"]
        self.assertEqual(problem["attempts"], 1)
        self.assertTrue(problem["first_try"])
        self.assertEqual(problem["best_time_sec"], 30)
        self.assertEqual(progress["streak"]["current"], 2)


if __name__ == "__main__":
    unittest.main()
