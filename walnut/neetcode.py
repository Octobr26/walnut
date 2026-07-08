from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_URL = "https://neetcode.io/roadmap"
LEETCODE_BASE = "https://leetcode.com/problems/"
NEETCODE_PROBLEMS_BASE = "https://neetcode.io/problems/"


@dataclass(frozen=True)
class RoadmapProblem:
    order: int
    title: str
    topic: str
    difficulty: str
    leetcode: int
    leetcode_url: str
    neetcode_url: str
    code: str


def _read_url(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8", "ignore")


def _script_url_from_html(html: str, base_url: str = "https://neetcode.io/") -> str:
    matches = re.findall(r'(?:src|href)="([^"]*main\.[^"]+\.js)"', html)
    if not matches:
        raise ValueError("could not find NeetCode main JavaScript bundle")
    script = matches[-1]
    if script.startswith("http"):
        return script
    if script.startswith("/"):
        return base_url.rstrip("/") + script
    return base_url.rstrip("/") + "/" + script


def fetch_bundle() -> str:
    html = _read_url(ROADMAP_URL)
    return _read_url(_script_url_from_html(html))


def _extract_array(bundle: str) -> str:
    start = bundle.find("$=[{problem:")
    if start == -1:
        raise ValueError("could not find NeetCode problem metadata array")
    start = bundle.find("[", start)
    level = 0
    in_string = False
    escaped = False
    for index in range(start, len(bundle)):
        char = bundle[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "[":
            level += 1
        elif char == "]":
            level -= 1
            if level == 0:
                return bundle[start : index + 1]
    raise ValueError("unterminated NeetCode problem metadata array")


def _iter_object_literals(array_source: str) -> list[str]:
    objects: list[str] = []
    level = 0
    in_string = False
    escaped = False
    object_start: int | None = None
    for index, char in enumerate(array_source):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            if level == 0:
                object_start = index
            level += 1
        elif char == "}":
            level -= 1
            if level == 0 and object_start is not None:
                objects.append(array_source[object_start : index + 1])
                object_start = None
    return objects


def _field(obj: str, name: str) -> str | None:
    match = re.search(rf'{re.escape(name)}:"((?:\\.|[^"\\])*)"', obj)
    if not match:
        return None
    return bytes(match.group(1), "utf-8").decode("unicode_escape")


def _leetcode_id(code: str) -> int:
    return int(code.split("-", 1)[0])


def _clean_url(base: str, suffix: str, trailing: bool = False) -> str:
    url = base.rstrip("/") + "/" + suffix.strip("/")
    return url + "/" if trailing else url


def extract_neetcode_150(bundle: str) -> list[RoadmapProblem]:
    """Extract public NeetCode 150 metadata from the site bundle.

    This intentionally reads only roadmap metadata: title, topic, difficulty,
    LeetCode ID/link, NeetCode problem link, and order. It does not extract or
    store statements, explanations, code solutions, or paid content.
    """

    array_source = _extract_array(bundle)
    problems: list[RoadmapProblem] = []
    for obj in _iter_object_literals(array_source):
        if "neetcode150:!0" not in obj:
            continue
        code = _field(obj, "code")
        title = _field(obj, "problem")
        topic = _field(obj, "pattern")
        difficulty = _field(obj, "difficulty")
        link = _field(obj, "link")
        nc_link = _field(obj, "ncLink")
        if not all([code, title, topic, difficulty, link, nc_link]):
            continue
        problems.append(
            RoadmapProblem(
                order=len(problems) + 1,
                title=title or "",
                topic=topic or "",
                difficulty=difficulty or "",
                leetcode=_leetcode_id(code or "0"),
                leetcode_url=_clean_url(LEETCODE_BASE, link or "", trailing=True),
                neetcode_url=_clean_url(NEETCODE_PROBLEMS_BASE, nc_link or ""),
                code=code or "",
            )
        )
    return problems


def fetch_neetcode_150() -> list[RoadmapProblem]:
    problems = extract_neetcode_150(fetch_bundle())
    if len(problems) != 150:
        raise ValueError(f"expected 150 NeetCode problems, found {len(problems)}")
    return problems


def _local_problem_index(roadmap: dict[str, Any]) -> dict[int, tuple[dict[str, Any], dict[str, Any]]]:
    index: dict[int, tuple[dict[str, Any], dict[str, Any]]] = {}
    for topic in roadmap["topics"]:
        for problem in topic["problems"]:
            index[int(problem["leetcode"])] = (topic, problem)
    return index


def diff_roadmap_metadata(roadmap: dict[str, Any], scraped: list[RoadmapProblem]) -> list[dict[str, Any]]:
    index = _local_problem_index(roadmap)
    diffs: list[dict[str, Any]] = []
    for scraped_problem in scraped:
        if scraped_problem.leetcode not in index:
            diffs.append(
                {
                    "leetcode": scraped_problem.leetcode,
                    "field": "problem",
                    "local": None,
                    "scraped": scraped_problem.title,
                }
            )
            continue
        topic, local = index[scraped_problem.leetcode]
        checks = {
            "title": scraped_problem.title,
            "difficulty": scraped_problem.difficulty,
            "leetcode_url": scraped_problem.leetcode_url,
            "topic": scraped_problem.topic,
        }
        local_values = {
            "title": local.get("title"),
            "difficulty": local.get("difficulty"),
            "leetcode_url": local.get("leetcode_url"),
            "topic": topic.get("name"),
        }
        for field, scraped_value in checks.items():
            if local_values[field] != scraped_value:
                diffs.append(
                    {
                        "leetcode": scraped_problem.leetcode,
                        "field": field,
                        "local": local_values[field],
                        "scraped": scraped_value,
                    }
                )
    return diffs


def apply_metadata(root: Path, roadmap: dict[str, Any], scraped: list[RoadmapProblem]) -> int:
    """Apply safe metadata updates without touching statements/cases/references."""

    index = _local_problem_index(roadmap)
    updated = 0
    for scraped_problem in scraped:
        if scraped_problem.leetcode not in index:
            continue
        _topic, local = index[scraped_problem.leetcode]
        for key, value in {
            "title": scraped_problem.title,
            "difficulty": scraped_problem.difficulty,
            "leetcode_url": scraped_problem.leetcode_url,
        }.items():
            if local.get(key) != value:
                local[key] = value
                updated += 1
        problem_path = root / local["dir"] / "problem.json"
        if problem_path.exists():
            problem_json = json.loads(problem_path.read_text(encoding="utf-8"))
            for key, value in {
                "title": scraped_problem.title,
                "difficulty": scraped_problem.difficulty,
                "leetcode": scraped_problem.leetcode,
                "leetcode_url": scraped_problem.leetcode_url,
                "neetcode_url": scraped_problem.neetcode_url,
            }.items():
                if problem_json.get(key) != value:
                    problem_json[key] = value
                    updated += 1
            problem_path.write_text(json.dumps(problem_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / "roadmap.json").write_text(json.dumps(roadmap, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return updated
