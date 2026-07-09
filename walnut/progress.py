from __future__ import annotations

import datetime as dt
import time
from pathlib import Path
from typing import Any

from .repo import load_json, load_problem, solution_path, walnut_dir, write_json


TARGET_TIMES = {"Easy": 900, "Medium": 1800, "Hard": 2700}


def today_local() -> str:
    return dt.datetime.now().astimezone().date().isoformat()


def current_streak(progress: dict[str, Any], local_date: str | None = None) -> int:
    today = dt.date.fromisoformat(local_date or today_local())
    streak = progress.get("streak", {})
    active_days = set()
    for value in streak.get("active_days", []):
        try:
            active_days.add(dt.date.fromisoformat(value))
        except (TypeError, ValueError):
            continue

    if active_days:
        end = today if today in active_days else today - dt.timedelta(days=1)
        if end not in active_days:
            return 0
        count = 0
        cursor = end
        while cursor in active_days:
            count += 1
            cursor -= dt.timedelta(days=1)
        return count

    last = streak.get("last_solved_date")
    try:
        last_date = dt.date.fromisoformat(last) if last else None
    except (TypeError, ValueError):
        return 0
    if last_date in {today, today - dt.timedelta(days=1)}:
        return int(streak.get("current", 0))
    return 0


def default_progress() -> dict[str, Any]:
    return {
        "version": 1,
        "active": None,
        "problems": {},
        "streak": {
            "current": 0,
            "longest": 0,
            "last_solved_date": None,
            "active_days": [],
        },
    }


def default_problem_record(now: float | None = None) -> dict[str, Any]:
    return {
        "status": "unsolved",
        "attempts": 0,
        "test_runs": 0,
        "revealed_hints": 0,
        "revealed_solution": False,
        "first_seen_at": now,
        "solved_at": None,
        "first_try": False,
        "best_time_sec": None,
        "last_time_sec": None,
        "history": [],
        "review": {
            "due": None,
            "interval_days": 0,
            "ease": 2.5,
            "reps": 0,
            "lapses": 0,
        },
        "slowest_case_sec": None,
    }


def ensure_problem(progress: dict[str, Any], slug: str, now: float | None = None) -> dict[str, Any]:
    problems = progress.setdefault("problems", {})
    if slug not in problems:
        problems[slug] = default_problem_record(now)
    elif problems[slug].get("first_seen_at") is None and now is not None:
        problems[slug]["first_seen_at"] = now
    return problems[slug]


def progress_path(root: Path) -> Path:
    return walnut_dir(root) / "progress.json"


def selected_path(root: Path) -> Path:
    return walnut_dir(root) / "selected.json"


def load_progress(root: Path) -> dict[str, Any]:
    path = progress_path(root)
    if not path.exists():
        return default_progress()
    return load_json(path)


def save_progress(root: Path, progress: dict[str, Any]) -> None:
    write_json(progress_path(root), progress)


def load_selected(root: Path) -> dict[str, Any]:
    path = selected_path(root)
    if not path.exists():
        return {}
    return load_json(path)


def save_selected(root: Path, slug: str, now: float | None = None) -> None:
    write_json(selected_path(root), {"slug": slug, "updated_at": time.time() if now is None else now})


def arm_timer(
    progress: dict[str, Any],
    slug: str,
    now: float | None = None,
    target_sec: int | None = None,
    force: bool = False,
) -> tuple[bool, str | None]:
    now = time.time() if now is None else now
    active = progress.get("active")
    if active and active.get("slug") != slug and not force:
        return False, active.get("slug")
    if active and active.get("slug") == slug:
        return True, None
    new_active: dict[str, Any] = {"slug": slug, "started_at": now}
    if target_sec is not None:
        new_active["target_sec"] = target_sec
    progress["active"] = new_active
    return True, None


def start_problem(
    root: Path,
    ref: Any,
    *,
    problem: dict[str, Any] | None = None,
    force: bool = False,
) -> tuple[bool, str | None, dict[str, Any], Path, bool]:
    from .files import ensure_solution

    problem = load_problem(root, ref) if problem is None else problem
    state = load_progress(root)
    ok, active_slug = arm_timer(state, ref.slug, force=force)
    if not ok:
        return False, active_slug, state, solution_path(root, ref), False
    mark_attempted(state, ref.slug)
    save_progress(root, state)
    existed = solution_path(root, ref).exists()
    solution = ensure_solution(root, ref, problem)
    return True, None, state, solution, existed


def mark_attempted(progress: dict[str, Any], slug: str, now: float | None = None) -> dict[str, Any]:
    now = time.time() if now is None else now
    record = ensure_problem(progress, slug, now)
    if record["status"] == "unsolved":
        record["status"] = "attempted"
    return record


def reveal_hint(progress: dict[str, Any], slug: str, count: int, now: float | None = None) -> None:
    record = ensure_problem(progress, slug, time.time() if now is None else now)
    record["revealed_hints"] = max(int(record.get("revealed_hints", 0)), count)


def reveal_solution(progress: dict[str, Any], slug: str, now: float | None = None) -> None:
    record = ensure_problem(progress, slug, time.time() if now is None else now)
    record["revealed_solution"] = True


def update_streak(progress: dict[str, Any], local_date: str) -> None:
    streak = progress.setdefault("streak", default_progress()["streak"])
    last = streak.get("last_solved_date")
    active_days = set(streak.get("active_days", []))
    if local_date in active_days:
        return

    current = int(streak.get("current", 0))
    if last:
        last_date = dt.date.fromisoformat(last)
        solve_date = dt.date.fromisoformat(local_date)
        if (solve_date - last_date).days == 1:
            current += 1
        elif (solve_date - last_date).days > 1:
            current = 1
        else:
            current = max(1, current)
    else:
        current = 1

    active_days.add(local_date)
    streak["current"] = current
    streak["longest"] = max(int(streak.get("longest", 0)), current)
    streak["last_solved_date"] = local_date
    streak["active_days"] = sorted(active_days)


def quality_score(
    *,
    failed_before_solve: int,
    revealed_hints: int,
    revealed_solution: bool,
    time_sec: int | None,
    target_sec: int | None,
) -> int:
    if revealed_solution:
        return 1
    if failed_before_solve == 0 and revealed_hints == 0:
        if time_sec is None or target_sec is None or time_sec <= target_sec:
            return 5
        return 4
    if revealed_hints <= 1 or failed_before_solve == 1:
        return 3
    return 2


def schedule_review(record: dict[str, Any], local_date: str, q: int) -> None:
    review = record.setdefault("review", default_problem_record()["review"])
    prev_interval = int(review.get("interval_days", 0) or 0)
    reps = int(review.get("reps", 0)) + 1
    if reps == 1:
        interval = 1
    elif reps == 2:
        interval = 3
    elif reps == 3:
        interval = 7
    else:
        interval = round(prev_interval * float(review.get("ease", 2.5)))

    ease = float(review.get("ease", 2.5))
    ease = max(1.3, min(3.0, ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))))
    due = dt.date.fromisoformat(local_date) + dt.timedelta(days=interval)
    review.update({"due": due.isoformat(), "interval_days": interval, "ease": ease, "reps": reps})


def record_test_result(
    progress: dict[str, Any],
    *,
    slug: str,
    passed: bool,
    cases_passed: int,
    cases_total: int,
    now: float,
    local_date: str,
    time_sec: int | None,
    target_sec: int | None,
    revealed_hints: int,
    revealed_solution: bool,
    slowest_case_sec: float | None,
    result: str | None = None,
) -> dict[str, Any]:
    record = ensure_problem(progress, slug, now)
    already_solved = record.get("status") == "solved"
    record["test_runs"] = int(record.get("test_runs", 0)) + 1
    record["revealed_hints"] = max(int(record.get("revealed_hints", 0)), revealed_hints)
    record["revealed_solution"] = bool(record.get("revealed_solution")) or revealed_solution
    if slowest_case_sec is not None:
        previous = record.get("slowest_case_sec")
        record["slowest_case_sec"] = slowest_case_sec if previous is None else max(float(previous), slowest_case_sec)

    history_result = result or ("pass" if passed else "fail")
    record.setdefault("history", []).append(
        {
            "at": now,
            "time_sec": time_sec,
            "result": history_result,
            "cases_passed": cases_passed,
            "cases_total": cases_total,
        }
    )

    if passed:
        if not already_solved:
            failed_before = int(record.get("attempts", 0))
            record["attempts"] = failed_before + 1
            record["status"] = "solved"
            record["solved_at"] = now
            record["first_try"] = (
                failed_before == 0
                and int(record.get("revealed_hints", 0)) == 0
                and not bool(record.get("revealed_solution"))
            )
        else:
            failed_before = max(0, int(record.get("attempts", 1)) - 1)

        if time_sec is not None:
            record["last_time_sec"] = time_sec
            best = record.get("best_time_sec")
            record["best_time_sec"] = time_sec if best is None else min(int(best), time_sec)

        q = quality_score(
            failed_before_solve=failed_before,
            revealed_hints=int(record.get("revealed_hints", 0)),
            revealed_solution=bool(record.get("revealed_solution")),
            time_sec=time_sec,
            target_sec=target_sec,
        )
        schedule_review(record, local_date, q)
        update_streak(progress, local_date)
        if (progress.get("active") or {}).get("slug") == slug:
            progress["active"] = None
    else:
        if not already_solved:
            record["status"] = "attempted"
            record["attempts"] = int(record.get("attempts", 0)) + 1

    return record


def record_run(root: Path, ref: Any, problem: dict[str, Any], result: Any) -> tuple[dict[str, Any], dict[str, Any], int | None]:
    state = load_progress(root)
    active = state.get("active")
    now = time.time()
    elapsed: int | None = None
    if active and active.get("slug") == ref.slug:
        elapsed = int(now - float(active["started_at"]))
    record = ensure_problem(state, ref.slug, now)
    target_sec = int(active["target_sec"]) if active and active.get("target_sec") else TARGET_TIMES.get(problem.get("difficulty", "Medium"), 1800)
    saved_record = record_test_result(
        state,
        slug=ref.slug,
        passed=result.ok,
        cases_passed=result.passed,
        cases_total=result.total,
        now=now,
        local_date=today_local(),
        time_sec=elapsed,
        target_sec=target_sec,
        revealed_hints=int(record.get("revealed_hints", 0)),
        revealed_solution=bool(record.get("revealed_solution")),
        slowest_case_sec=result.slowest_case_sec,
        result="pass" if result.ok else ("timeout" if result.timed_out else "fail"),
    )
    save_progress(root, state)
    return state, saved_record, elapsed


def reset_problem(root: Path, progress: dict[str, Any], slug: str, solution_path: Path, hard: bool = False) -> None:
    if solution_path.exists():
        solution_path.unlink()
    if (progress.get("active") or {}).get("slug") == slug:
        progress["active"] = None
    if hard:
        progress.get("problems", {}).pop(slug, None)
        return

    record = ensure_problem(progress, slug)
    keep = {
        "history": record.get("history", []),
        "review": record.get("review", default_problem_record()["review"]),
    }
    record.update(default_problem_record(record.get("first_seen_at")))
    record.update(keep)
    record["status"] = "unsolved"
