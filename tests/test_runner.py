from __future__ import annotations

import json
import shutil
import sys
import threading
from pathlib import Path
from textwrap import dedent

import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def clean_tmp(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


class RunnerTests(unittest.TestCase):
    def make_problem(self, tmp: Path) -> dict:
        (tmp / "solution.py").write_text(
            dedent(
                """
                class Solution:
                    def add(self, nums):
                        nums.append(99)
                        return sum(nums[:-1])
                """
            ).strip()
            + "\n"
        )
        return {
            "runner": {
                "entry": "method",
                "method": "add",
                "compare": "exact",
                "timeout_sec": 1,
            },
            "cases": [
                {"kind": "example", "args": {"nums": [1, 2]}, "expected": 3},
                {"kind": "edge", "args": {"nums": [1, 2]}, "expected": 3},
            ],
        }

    def test_deep_copies_case_args_between_runs(self):
        from walnut.runner import run

        tmp = ROOT / ".tmp-runner-deepcopy"
        tmp.mkdir(exist_ok=True)
        try:
            result = run(tmp, self.make_problem(tmp))
            self.assertEqual(result.passed, 2)
            self.assertEqual(result.total, 2)
        finally:
            clean_tmp(tmp)

    def test_verify_can_run_reference_module(self):
        from walnut.runner import run

        tmp = ROOT / ".tmp-runner-reference"
        tmp.mkdir(exist_ok=True)
        try:
            (tmp / "reference.py").write_text(
                "class Solution:\n    def echo(self, value):\n        return value\n"
            )
            problem = {
                "runner": {
                    "entry": "method",
                    "method": "echo",
                    "compare": "exact",
                    "timeout_sec": 1,
                },
                "cases": [{"args": {"value": 7}, "expected": 7}],
            }
            result = run(tmp, problem, module_filename="reference.py")
            self.assertTrue(result.ok)
        finally:
            clean_tmp(tmp)

    def test_generated_case_uses_fixtures(self):
        from walnut.runner import run

        tmp = ROOT / ".tmp-runner-fixture"
        tmp.mkdir(exist_ok=True)
        try:
            (tmp / "solution.py").write_text(
                "class Solution:\n    def double(self, value):\n        return value * 2\n"
            )
            (tmp / "fixtures.py").write_text(
                "def make_case(seed):\n    return {'args': {'value': seed}, 'expected': seed * 2}\n"
            )
            problem = {
                "runner": {
                    "entry": "method",
                    "method": "double",
                    "compare": "exact",
                    "timeout_sec": 1,
                },
                "cases": [{"kind": "stress", "gen": {"fn": "make_case", "seed": 21}}],
            }
            result = run(tmp, problem)
            self.assertTrue(result.ok)
        finally:
            clean_tmp(tmp)

    def test_timeout_in_worker_thread_returns_without_waiting_for_user_code(self):
        from walnut.runner import run

        tmp = ROOT / ".tmp-runner-timeout-thread"
        tmp.mkdir(exist_ok=True)
        try:
            (tmp / "solution.py").write_text(
                "import time\nclass Solution:\n    def slow(self):\n        time.sleep(2)\n        return 1\n"
            )
            problem = {
                "runner": {
                    "entry": "method",
                    "method": "slow",
                    "compare": "exact",
                    "timeout_sec": 0.05,
                },
                "cases": [{"args": {}, "expected": 1}],
            }
            result_holder = {}

            def target() -> None:
                result_holder["result"] = run(tmp, problem)

            thread = threading.Thread(target=target)
            thread.start()
            thread.join(1)

            self.assertFalse(thread.is_alive())
            result = result_holder["result"]
            self.assertFalse(result.ok)
            self.assertTrue(result.timed_out)
            self.assertTrue(result.failures[0].timed_out)
            self.assertIn("timed out after", result.failures[0].error)
        finally:
            clean_tmp(tmp)


if __name__ == "__main__":
    unittest.main()
