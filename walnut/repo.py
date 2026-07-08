from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class RepoError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProblemRef:
    id: int
    slug: str
    title: str
    difficulty: str
    leetcode: int
    leetcode_url: str
    method: str | None
    seeded: bool
    dir: str
    topic_id: int
    topic_slug: str
    topic_name: str

    @property
    def path(self) -> Path:
        return Path(self.dir)


def find_root(start: Path | None = None) -> Path:
    env = os.environ.get("WALNUT_HOME")
    if env:
        candidate = Path(env).expanduser().resolve()
        if (candidate / "roadmap.json").is_file():
            return candidate
        raise RepoError(f"WALNUT_HOME is set but no roadmap.json was found: {candidate}")

    current = (start or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / "roadmap.json").is_file():
            return parent

    package_root = Path(__file__).resolve().parents[1]
    if (package_root / "roadmap.json").is_file():
        return package_root

    raise RepoError("run inside the walnut repo or set WALNUT_HOME")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")


def load_roadmap(root: Path) -> dict[str, Any]:
    return load_json(root / "roadmap.json")


def iter_problem_refs(roadmap: dict[str, Any]) -> Iterable[ProblemRef]:
    for topic in roadmap["topics"]:
        for problem in topic["problems"]:
            yield ProblemRef(
                id=int(problem["id"]),
                slug=problem["slug"],
                title=problem["title"],
                difficulty=problem["difficulty"],
                leetcode=int(problem["leetcode"]),
                leetcode_url=problem["leetcode_url"],
                method=problem.get("method"),
                seeded=bool(problem.get("seeded")),
                dir=problem["dir"],
                topic_id=int(topic["id"]),
                topic_slug=topic["slug"],
                topic_name=topic["name"],
            )


def all_problem_refs(root: Path) -> list[ProblemRef]:
    return list(iter_problem_refs(load_roadmap(root)))


def resolve_problem(root: Path, token: str | int) -> ProblemRef:
    refs = all_problem_refs(root)
    text = str(token).strip()
    if text.isdigit():
        pid = int(text)
        for ref in refs:
            if ref.id == pid:
                return ref
        raise KeyError(f"problem not found: {token}")

    exact = [ref for ref in refs if ref.slug == text]
    if len(exact) == 1:
        return exact[0]

    matches = [ref for ref in refs if ref.slug.startswith(text)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        names = ", ".join(f"{ref.id}:{ref.slug}" for ref in matches[:8])
        raise ValueError(f"ambiguous problem prefix '{text}': {names}")
    raise KeyError(f"problem not found: {token}")


def resolve_topic(roadmap: dict[str, Any], token: str | None) -> dict[str, Any] | None:
    if token is None:
        return None
    text = token.strip().lower()
    topics = roadmap["topics"]
    if text.isdigit():
        tid = int(text)
        for topic in topics:
            if int(topic["id"]) == tid:
                return topic
        raise KeyError(f"topic not found: {token}")

    exact = [
        topic
        for topic in topics
        if topic["slug"].lower() == text or topic["name"].lower() == text
    ]
    if len(exact) == 1:
        return exact[0]

    matches = [
        topic
        for topic in topics
        if topic["slug"].lower().startswith(text) or topic["name"].lower().startswith(text)
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        names = ", ".join(topic["slug"] for topic in matches)
        raise ValueError(f"ambiguous topic '{token}': {names}")
    raise KeyError(f"topic not found: {token}")


def problem_dir(root: Path, ref: ProblemRef) -> Path:
    return root / ref.dir


def load_problem(root: Path, ref: ProblemRef) -> dict[str, Any]:
    return load_json(problem_dir(root, ref) / "problem.json")


def walnut_dir(root: Path) -> Path:
    return root / ".walnut"
