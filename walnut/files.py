from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

from .repo import ProblemRef, load_problem, problem_dir, solution_path


HEADER_MARKER = "# Walnut problem:"


def _comment_block(label: str, value: str, width: int = 88) -> list[str]:
    if not value:
        return []
    lines = [f"# {label}:"]
    for paragraph in value.splitlines():
        if not paragraph.strip():
            lines.append("#")
            continue
        for line in textwrap.wrap(paragraph, width=width):
            lines.append(f"#   {line}")
    return lines


def solution_header(root: Path, ref: ProblemRef, problem: dict[str, Any] | None = None) -> str:
    problem = load_problem(root, ref) if problem is None else problem
    lines = [
        f"{HEADER_MARKER} #{ref.id} {ref.title}",
        f"# Difficulty: {ref.difficulty}",
        f"# Topic: {ref.topic_name}",
        f"# LeetCode: {ref.leetcode_url}",
    ]

    statement = str(problem.get("statement") or "").strip()
    if statement:
        lines.append("#")
        lines.extend(_comment_block("Requirements", statement))

    examples = problem.get("examples") or []
    if examples:
        lines.append("#")
        lines.append("# Examples:")
        for index, example in enumerate(examples[:3], start=1):
            lines.append(f"#   {index}. input: {example.get('input')}")
            lines.append(f"#      output: {example.get('output')}")

    constraints = problem.get("constraints") or []
    if constraints:
        lines.append("#")
        lines.append("# Constraints:")
        for constraint in constraints:
            lines.append(f"#   - {constraint}")

    return "\n".join(lines).rstrip() + "\n"


def ensure_solution(root: Path, ref: ProblemRef, problem: dict[str, Any] | None = None) -> Path:
    pdir = problem_dir(root, ref)
    solution = solution_path(root, ref)
    header = solution_header(root, ref, problem)

    if not solution.exists():
        starter = (pdir / "starter.py").read_text(encoding="utf-8")
        solution.write_text(f"{header}\n{starter}", encoding="utf-8")
        return solution

    current = solution.read_text(encoding="utf-8")
    if not current.startswith(HEADER_MARKER):
        solution.write_text(f"{header}\n{current}", encoding="utf-8")
    return solution


def ensure_notes(root: Path, ref: ProblemRef) -> Path:
    notes = problem_dir(root, ref) / "notes.md"
    if not notes.exists():
        notes.write_text(
            f"# {ref.title} Notes\n\n"
            f"- LeetCode: {ref.leetcode_url}\n\n"
            "## Approach\n\n"
            "## Mistakes\n\n"
            "## Review\n",
            encoding="utf-8",
        )
    return notes
