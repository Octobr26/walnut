from __future__ import annotations

import argparse
import json
import os
import platform
import random
import shlex
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Any

from . import __version__
from . import neetcode
from .files import ensure_notes, ensure_solution
from .format import (
    failure_by_case as _failure_by_case,
    format_time as _format_time,
    progress_text as _progress_text,
    short as _short,
    status_for as _status_for,
    target_for as _target_for,
)
from . import progress as progress_mod
from .repo import (
    RepoError,
    all_problem_refs,
    cheatsheet_path,
    find_root,
    load_problem,
    load_roadmap,
    problem_dir,
    resolve_problem,
    resolve_topic,
    solution_path,
    walnut_dir,
)
from .runner import RunResult, run, validate_problem

try:
    from rich import box
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except Exception:
    box = Console = Group = Panel = Table = Text = None  # type: ignore[assignment]
    RICH_AVAILABLE = False


def _strip_global_flags(argv: list[str]) -> tuple[list[str], dict[str, bool]]:
    flags = {"plain": False, "json": False, "debug": False}
    kept: list[str] = []
    for arg in argv:
        if arg == "--plain":
            flags["plain"] = True
        elif arg == "--json":
            flags["json"] = True
        elif arg == "--debug":
            flags["debug"] = True
        else:
            kept.append(arg)
    return kept, flags


def _print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def _console(flags: dict[str, bool]) -> Any | None:
    if flags.get("plain") or flags.get("json") or not RICH_AVAILABLE:
        return None
    return Console(highlight=False)


def _root_or_exit() -> Path:
    try:
        return find_root()
    except RepoError as exc:
        print(f"error: {exc}")
        raise SystemExit(3)


def _next_ref(refs: list[Any], progress: dict[str, Any]) -> Any | None:
    seeded = [ref for ref in refs if ref.seeded and _status_for(progress, ref.slug) != "solved"]
    pool = seeded or [ref for ref in refs if _status_for(progress, ref.slug) != "solved"]
    return pool[0] if pool else None


def _difficulty(value: str) -> Any:
    styles = {"Easy": "green", "Medium": "yellow", "Hard": "red"}
    if Text is None:
        return value
    return Text(value, style=f"bold {styles.get(value, 'white')}")


def _status(value: str) -> Any:
    styles = {"solved": "bold green", "attempted": "bold yellow", "unsolved": "dim"}
    if Text is None:
        return value
    return Text(value, style=styles.get(value, "white"))


def _pass_fail(ok: bool) -> Any:
    if Text is None:
        return "PASS" if ok else "FAIL"
    return Text("PASS" if ok else "FAIL", style="bold green" if ok else "bold red")


def _print_run_result(problem: dict[str, Any], result: RunResult, perf: bool = False, flags: dict[str, bool] | None = None) -> None:
    console = _console(flags or {"plain": True, "json": False, "debug": False})
    if console:
        failures = _failure_by_case(result)
        title = f"#{problem['id']} {problem['title']}"
        summary = Table.grid(expand=True)
        summary.add_column(ratio=2)
        summary.add_column(justify="right")
        summary.add_row(
            f"[bold]{problem['topic']}[/]",
            f"{result.passed}/{result.total} cases",
        )
        summary.add_row(
            f"difficulty: {problem['difficulty']}",
            "passed" if result.ok else "needs work",
        )
        console.print(
            Panel(
                summary,
                title=f"[bold]{title}[/]",
                subtitle="[green]all clear[/]" if result.ok else "[red]failing cases below[/]",
                border_style="green" if result.ok else "red",
            )
        )

        if result.elapsed_by_case:
            table = Table(box=box.ROUNDED, expand=True)
            table.add_column("Result", no_wrap=True)
            table.add_column("Case", justify="right", no_wrap=True)
            table.add_column("Kind", no_wrap=True)
            table.add_column("Note")
            if perf:
                table.add_column("Time", justify="right", no_wrap=True)
            for item in result.elapsed_by_case:
                failure = failures.get(item["index"])
                row = [
                    _pass_fail(failure is None),
                    str(item["index"]),
                    item["kind"],
                    Text(item.get("note") or "", style="dim"),
                ]
                if perf:
                    row.append(f"{item['elapsed']:.3f}s / {item['timeout_sec']:g}s")
                table.add_row(*row)
            console.print(table)
        elif result.failures:
            console.print(Panel("Import failed before cases could run.", border_style="red"))

        for failure in result.failures:
            details = Text()
            if failure.note:
                details.append(f"note      {failure.note}\n")
            if failure.args is not None:
                details.append(f"input     {_short(failure.args)}\n")
            if failure.expected is not None:
                details.append(f"expected  {_short(failure.expected)}\n")
            if failure.got is not None:
                details.append(f"got       {_short(failure.got)}\n")
            if failure.error:
                details.append(f"error     {failure.error}\n", style="red")
            console.print(
                Panel(
                    details,
                    title=f"case {failure.index}: {failure.kind}",
                    border_style="red",
                )
            )

        if result.slowest_case_sec is not None:
            console.print(f"[dim]slowest case: {result.slowest_case_sec:.3f}s[/]")
        if not result.ok:
            console.print("[dim]Try: walnut hint {0}  |  walnut open-official {0} --site leetcode[/]".format(problem["id"]))
        return

    print(f"{problem['title']} · {problem['difficulty']} · {problem['topic']}")
    for item in result.elapsed_by_case:
        marker = "ok"
        for failure in result.failures:
            if failure.index == item["index"]:
                marker = "FAIL"
                break
        note = f" ({item['note']})" if item.get("note") else ""
        timing = f" {item['elapsed']:.3f}s/{item['timeout_sec']:g}s" if perf else ""
        print(f"  {marker:4} case {item['index']} [{item['kind']}]{note}{timing}")

    if not result.elapsed_by_case and result.failures:
        print("  FAIL import")

    for failure in result.failures:
        print(f"    case {failure.index}: {failure.kind}")
        if failure.note:
            print(f"      note      {failure.note}")
        if failure.args is not None:
            print(f"      input     {_short(failure.args)}")
        if failure.expected is not None:
            print(f"      expected  {_short(failure.expected)}")
        if failure.got is not None:
            print(f"      got       {_short(failure.got)}")
        if failure.error:
            print(f"      error     {failure.error}")

    if result.slowest_case_sec is not None:
        print(f"  slowest: {result.slowest_case_sec:.3f}s")
    print(f"  {result.passed}/{result.total} cases passing")


def cmd_doctor(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    roadmap = load_roadmap(root)
    refs = all_problem_refs(root)
    state_dir = walnut_dir(root)
    state_dir.mkdir(exist_ok=True)
    writable = os.access(state_dir, os.W_OK)
    data = {
        "python": platform.python_version(),
        "rich": RICH_AVAILABLE,
        "repo": str(root),
        "seeded": sum(1 for ref in refs if ref.seeded),
        "total": len(refs),
        "walnut_dir_writable": writable,
    }
    if flags["json"]:
        _print_json(data)
    elif (console := _console(flags)):
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold cyan", no_wrap=True)
        table.add_column()
        table.add_row("Python", data["python"])
        table.add_row("Rich", "yes" if RICH_AVAILABLE else "no, plain fallback")
        table.add_row("Repo", str(root))
        table.add_row("Problems", f"{data['seeded']}/{data['total']} seeded")
        table.add_row("State", ".walnut writable" if writable else ".walnut not writable")
        table.add_row("Topics", str(len(roadmap["topics"])))
        console.print(
            Panel(
                table,
                title="[bold]Walnut Doctor[/]",
                subtitle="[green]ready[/]" if writable else "[red]needs attention[/]",
                border_style="green" if writable else "red",
            )
        )
    else:
        print(f"Python: {data['python']}")
        print(f"rich: {'yes' if RICH_AVAILABLE else 'no, plain fallback'}")
        print(f"repo: {root}")
        print(f"problems: {data['seeded']}/{data['total']} seeded")
        print(f".walnut writable: {'yes' if writable else 'no'}")
        print(f"topics: {len(roadmap['topics'])}")
    return 0 if writable else 3


def cmd_topics(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    roadmap = load_roadmap(root)
    progress = progress_mod.load_progress(root)
    rows = []
    for topic in roadmap["topics"]:
        total = len(topic["problems"])
        solved = sum(1 for item in topic["problems"] if _status_for(progress, item["slug"]) == "solved")
        ready = sum(1 for item in topic["problems"] if item.get("seeded"))
        rows.append(
            {
                "id": topic["id"],
                "name": topic["name"],
                "solved": solved,
                "total": total,
                "ready": ready,
            }
        )
    if flags["json"]:
        _print_json(rows)
    elif (console := _console(flags)):
        table = Table(title="Walnut Roadmap", box=box.HEAVY_HEAD, expand=True)
        table.add_column("#", justify="right", style="dim", no_wrap=True)
        table.add_column("Topic", style="bold")
        table.add_column("Progress", no_wrap=True)
        table.add_column("Solved", justify="right", no_wrap=True)
        table.add_column("Local Tests", justify="right", no_wrap=True)
        for row in rows:
            table.add_row(
                str(row["id"]),
                row["name"],
                _progress_text(row["solved"], row["total"]),
                f"{row['solved']}/{row['total']}",
                f"{row['ready']}/{row['total']}",
            )
        solved_total = sum(row["solved"] for row in rows)
        total = sum(row["total"] for row in rows)
        ready_total = sum(row["ready"] for row in rows)
        console.print(
            Panel(
                f"[bold]{solved_total}/{total} solved[/]   [cyan]{ready_total} ready locally[/]   [dim]use --plain for script output[/]",
                border_style="cyan",
            )
        )
        console.print(table)
    else:
        print(f"{len(rows)} topics · {sum(row['total'] for row in rows)} problems")
        for row in rows:
            print(
                f"{row['id']:>2}. {row['name']:<34} "
                f"{row['solved']:>2}/{row['total']:<2} solved · {row['ready']:>2} ready"
            )
    return 0


def cmd_list(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    roadmap = load_roadmap(root)
    topic = resolve_topic(roadmap, args.topic) if args.topic else None
    progress = progress_mod.load_progress(root)
    refs = all_problem_refs(root)
    if topic:
        refs = [ref for ref in refs if ref.topic_slug == topic["slug"]]
    if args.ready:
        refs = [ref for ref in refs if ref.seeded]
    if args.difficulty:
        refs = [ref for ref in refs if ref.difficulty.lower() == args.difficulty.lower()]
    if args.status:
        refs = [ref for ref in refs if _status_for(progress, ref.slug) == args.status]

    rows = [
        {
            "id": ref.id,
            "status": _status_for(progress, ref.slug),
            "title": ref.title,
            "difficulty": ref.difficulty,
            "topic": ref.topic_name,
            "seeded": ref.seeded,
            "slug": ref.slug,
        }
        for ref in refs
    ]
    if flags["json"]:
        _print_json(rows)
    elif (console := _console(flags)):
        title = topic["name"] if topic else "Problems"
        table = Table(title=title, box=box.ROUNDED, expand=True)
        table.add_column("#", justify="right", style="dim", no_wrap=True)
        table.add_column("Status", no_wrap=True)
        table.add_column("Title", style="bold")
        table.add_column("Difficulty", no_wrap=True)
        table.add_column("Topic")
        table.add_column("Local", justify="center", no_wrap=True)
        for row in rows:
            table.add_row(
                str(row["id"]),
                _status(row["status"]),
                row["title"],
                _difficulty(row["difficulty"]),
                row["topic"],
                Text("ready", style="green") if row["seeded"] and Text else ("ready" if row["seeded"] else "link"),
            )
        console.print(table)
        console.print("[dim]Try: walnut show <id>  |  walnut pick <id>[/]")
    else:
        for row in rows:
            tags = [] if row["seeded"] else ["no local tests"]
            tag_text = f" [{' · '.join(tags)}]" if tags else ""
            print(
                f"{row['id']:>3}. {row['status']:<9} {row['title']:<42} "
                f"{row['difficulty']:<6} {row['topic']}{tag_text}"
            )
    return 0


def cmd_show(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    ref = resolve_problem(root, args.id)
    problem = load_problem(root, ref)
    if flags["json"]:
        _print_json(problem)
        return 0
    if (console := _console(flags)):
        header = Table.grid(expand=True)
        header.add_column(ratio=2)
        header.add_column(justify="right")
        header.add_row(
            f"[bold]#{problem['id']} {problem['title']}[/]",
            f"{problem['difficulty']}  [dim]{problem['topic']}[/]",
        )
        console.print(Panel(header, border_style="cyan"))
        console.print(
            Panel(
                Text(problem.get("statement") or "Statement coming soon."),
                title="Problem",
                border_style="cyan",
            )
        )
        if problem.get("examples"):
            examples = Table(title="Examples", box=box.ROUNDED, expand=True)
            examples.add_column("#", justify="right", style="dim", no_wrap=True)
            examples.add_column("Input")
            examples.add_column("Output")
            examples.add_column("Explanation")
            for index, ex in enumerate(problem["examples"], start=1):
                examples.add_row(
                    str(index),
                    Text(str(ex["input"])),
                    Text(str(ex["output"])),
                    Text(str(ex.get("explanation") or "")),
                )
            console.print(examples)
        if problem.get("constraints"):
            console.print(
                Panel(
                    Text("\n".join(f"- {constraint}" for constraint in problem["constraints"])),
                    title="Constraints",
                    border_style="magenta",
                )
            )
        links = Table.grid(padding=(0, 2))
        links.add_column(style="bold cyan", no_wrap=True)
        links.add_column()
        links.add_row("LeetCode", problem["leetcode_url"])
        if problem.get("neetcode_url"):
            links.add_row("NeetCode", problem["neetcode_url"])
        links.add_row("Try next", f"walnut pick {problem['id']}  |  walnut test {problem['id']} --perf")
        console.print(Panel(links, title="Links and commands", border_style="green"))
        if not problem.get("seeded"):
            console.print("[yellow]Not seeded yet: local tests, hints, and reference solution are not available.[/]")
        return 0
    print(f"#{problem['id']} · {problem['title']} · {problem['difficulty']} · {problem['topic']}")
    print()
    print(problem.get("statement") or "Statement coming soon.")
    print()
    if problem.get("examples"):
        print("Examples")
        for index, ex in enumerate(problem["examples"], start=1):
            print(f"  {index}. input: {ex['input']}")
            print(f"     output: {ex['output']}")
            if ex.get("explanation"):
                print(f"     {ex['explanation']}")
        print()
    if problem.get("constraints"):
        print("Constraints")
        for constraint in problem["constraints"]:
            print(f"  - {constraint}")
        print()
    print(f"LeetCode: {problem['leetcode_url']}")
    if not problem.get("seeded"):
        print("Not seeded yet: local tests, hints, and reference solution are not available.")
    return 0


def _launch_editor(path: Path) -> None:
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if not editor:
        for candidate in ("nano", "vim", "notepad"):
            if shutil.which(candidate):
                editor = candidate
                break
    if not editor:
        print(f"edit: {path}")
        return
    cmd = shlex.split(editor) + [str(path)]
    completed = subprocess.run(cmd, check=False)
    if completed.returncode != 0:
        print(f"warning: editor exited with code {completed.returncode}")


def cmd_pick(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    ref = resolve_problem(root, args.id)
    problem = load_problem(root, ref)
    ok, active_slug, state, solution, existed = progress_mod.start_problem(root, ref, problem=problem, force=args.force)
    if not ok:
        print(f"timer already active for {active_slug}; rerun with --force to replace it")
        return 2
    if (console := _console(flags)):
        info = Table.grid(padding=(0, 2))
        info.add_column(style="bold cyan", no_wrap=True)
        info.add_column()
        info.add_row("Problem", f"#{ref.id} {ref.title}")
        info.add_row("Difficulty", ref.difficulty)
        info.add_row("Topic", ref.topic_name)
        info.add_row("Solution", str(solution))
        info.add_row("Target", _format_time(_target_for(problem, state.get("active"))))
        info.add_row("Tests", "ready" if problem.get("seeded") else "link only")
        console.print(
            Panel(
                info,
                title="[bold]Picked[/]" if existed else "[bold]Created solution file[/]",
                subtitle=f"walnut test {ref.id} --perf",
                border_style="green" if problem.get("seeded") else "yellow",
            )
        )
        if not problem.get("seeded"):
            console.print("[yellow]Not seeded yet: see the LeetCode link; local tests are unavailable.[/]")
    else:
        print(f"ready: {solution}" if existed else f"created: {solution}")
        if not problem.get("seeded"):
            print("warning: not seeded yet - see the LeetCode link; local tests are unavailable")
    if args.open:
        _launch_editor(solution)
    return 0


def cmd_open(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    ref = resolve_problem(root, args.id)
    problem = load_problem(root, ref)
    ok, active_slug, _state, solution, _existed = progress_mod.start_problem(root, ref, problem=problem, force=args.force)
    if not ok:
        print(f"timer already active for {active_slug}; rerun with --force to replace it")
        return 2
    if not problem.get("seeded"):
        print("warning: not seeded yet - see the LeetCode link; local tests are unavailable")
    _launch_editor(solution)
    return 0


def _run_problem(root: Path, ref: Any, mutate: bool, perf: bool = False, flags: dict[str, bool] | None = None) -> int:
    problem = load_problem(root, ref)
    if not problem.get("seeded"):
        print(f"{ref.title} is not seeded yet - see the LeetCode link: {ref.leetcode_url}")
        return 2
    result = run(problem_dir(root, ref), problem)
    flags = flags or {"plain": True, "json": False, "debug": False}
    _print_run_result(problem, result, perf=perf, flags=flags)
    if mutate:
        _state, record, elapsed = progress_mod.record_run(root, ref, problem, result)
        if result.ok:
            if (console := _console(flags)):
                console.print(
                    Panel(
                        f"[bold green]Solved[/]{f' in {_format_time(elapsed)}' if elapsed is not None else ''}. "
                        f"Review due: {record.get('review', {}).get('due', '--')}",
                        border_style="green",
                    )
                )
            else:
                print(f"Solved{f' in {_format_time(elapsed)}' if elapsed is not None else ''}.")
    return 0 if result.ok else 1


def cmd_test(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    ref = resolve_problem(root, args.id)
    return _run_problem(root, ref, mutate=True, perf=args.perf, flags=flags)


def cmd_run(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    ref = resolve_problem(root, args.id)
    return _run_problem(root, ref, mutate=False, perf=args.perf, flags=flags)


def cmd_hint(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    ref = resolve_problem(root, args.id)
    problem = load_problem(root, ref)
    if not problem.get("seeded"):
        print(f"{ref.title} is not seeded yet - see the LeetCode link: {ref.leetcode_url}")
        return 2
    hints = problem.get("hints", [])
    state = progress_mod.load_progress(root)
    record = progress_mod.ensure_problem(state, ref.slug, time.time())
    index = args.n if args.n is not None else (int(record.get("revealed_hints", 0)) + 1)
    if index < 1 or index > len(hints):
        print(f"hint {index} is not available")
        return 2
    progress_mod.reveal_hint(state, ref.slug, index)
    progress_mod.save_progress(root, state)
    print(f"Hint {index}: {hints[index - 1]}")
    return 0


def cmd_solution(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    ref = resolve_problem(root, args.id)
    problem = load_problem(root, ref)
    if not problem.get("seeded"):
        print(f"{ref.title} is not seeded yet - see the LeetCode link: {ref.leetcode_url}")
        return 2
    if not args.yes:
        answer = input("Show reference solution? [y/N] ").strip().lower()
        if answer != "y":
            return 0
    solution = (problem_dir(root, ref) / "reference.py").read_text(encoding="utf-8")
    state = progress_mod.load_progress(root)
    progress_mod.reveal_solution(state, ref.slug)
    progress_mod.save_progress(root, state)
    print(solution)
    return 0


def cmd_reset(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    ref = resolve_problem(root, args.id)
    state = progress_mod.load_progress(root)
    progress_mod.reset_problem(root, state, ref.slug, solution_path(root, ref), hard=args.hard)
    progress_mod.save_progress(root, state)
    print(f"reset {ref.title}{' (hard)' if args.hard else ''}")
    return 0


def _verify_one(root: Path, ref: Any) -> tuple[bool, str]:
    if not ref.seeded:
        return False, f"{ref.title} is not seeded yet - see the LeetCode link: {ref.leetcode_url}"
    problem = load_problem(root, ref)
    pdir = problem_dir(root, ref)
    errors = validate_problem(pdir, problem, module_filename="reference.py")
    if errors:
        return False, "; ".join(errors)
    result = run(pdir, problem, module_filename="reference.py")
    if not result.ok:
        details = "; ".join(f"case {f.index}: {f.error or f.got}" for f in result.failures)
        return False, details
    return True, "ok"


def cmd_verify(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    refs = [ref for ref in all_problem_refs(root) if ref.seeded] if args.all else [resolve_problem(root, args.id)]
    passed = 0
    rows = []
    for ref in refs:
        ok, message = _verify_one(root, ref)
        rows.append({"id": ref.id, "slug": ref.slug, "ok": ok, "message": message})
        if ok:
            passed += 1
        elif not flags["json"] and not _console(flags):
            print(f"FAIL {ref.id} {ref.title}: {message}")
    if flags["json"]:
        _print_json(rows)
    elif (console := _console(flags)):
        if passed == len(refs):
            console.print(
                Panel(
                    f"[bold green]{passed}/{len(refs)} seeded problems verified[/]",
                    title="Walnut Verify",
                    border_style="green",
                )
            )
        else:
            table = Table(title="Verification failures", box=box.ROUNDED, expand=True)
            table.add_column("#", justify="right", no_wrap=True)
            table.add_column("Slug")
            table.add_column("Message")
            for row in rows:
                if not row["ok"]:
                    table.add_row(str(row["id"]), row["slug"], row["message"])
            console.print(table)
    elif passed == len(refs):
        print(f"{passed}/{len(refs)} seeded problems verified")
    return 0 if passed == len(refs) else 1


def cmd_home(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    roadmap = load_roadmap(root)
    state = progress_mod.load_progress(root)
    refs = all_problem_refs(root)
    total = len(refs)
    ready = sum(1 for ref in refs if ref.seeded)
    solved = sum(1 for ref in refs if _status_for(state, ref.slug) == "solved")
    attempted = sum(1 for ref in refs if _status_for(state, ref.slug) == "attempted")
    next_ref = _next_ref(refs, state)
    streak = dict(state.get("streak", {}))
    streak["current"] = progress_mod.current_streak(state)
    active = state.get("active")

    data = {
        "solved": solved,
        "attempted": attempted,
        "ready": ready,
        "total": total,
        "streak": streak,
        "active": active,
        "next": None if next_ref is None else {"id": next_ref.id, "title": next_ref.title, "difficulty": next_ref.difficulty},
    }
    if flags["json"]:
        _print_json(data)
        return 0
    if not (console := _console(flags)):
        return cmd_next(args, flags)

    stats = Table.grid(expand=True)
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_row("[bold cyan]Solved[/]", "[bold yellow]Attempted[/]", "[bold green]Ready[/]", "[bold magenta]Streak[/]")
    stats.add_row(
        f"{solved}/{total}",
        str(attempted),
        f"{ready}/{total}",
        f"{streak.get('current', 0)} days",
    )
    console.print(Panel(stats, title="[bold]Walnut[/]", subtitle="offline NeetCode 150 practice", border_style="cyan"))

    if active:
        active_ref = next((ref for ref in refs if ref.slug == active.get("slug")), None)
        started = float(active.get("started_at", time.time()))
        elapsed = int(time.time() - started)
        target = int(active.get("target_sec") or (progress_mod.TARGET_TIMES.get(active_ref.difficulty, 1800) if active_ref else 1800))
        active_text = Table.grid(padding=(0, 2))
        active_text.add_column(style="bold cyan")
        active_text.add_column()
        active_text.add_row("Active", f"#{active_ref.id} {active_ref.title}" if active_ref else active.get("slug", "--"))
        active_text.add_row("Timer", f"{_format_time(elapsed)} / {_format_time(target)}")
        active_text.add_row("Run", f"walnut test {active_ref.id if active_ref else active.get('slug')} --perf")
        console.print(Panel(active_text, title="In progress", border_style="yellow"))

    if next_ref is not None:
        next_text = Table.grid(padding=(0, 2))
        next_text.add_column(style="bold cyan")
        next_text.add_column()
        next_text.add_row("Next", f"#{next_ref.id} {next_ref.title}")
        next_text.add_row("Difficulty", next_ref.difficulty)
        next_text.add_row("Topic", next_ref.topic_name)
        next_text.add_row("Start", f"walnut pick {next_ref.id}")
        next_text.add_row("Preview", f"walnut show {next_ref.id}")
        console.print(Panel(next_text, title="Next up", border_style="green"))
    else:
        console.print(Panel("[bold green]All problems solved.[/]", border_style="green"))

    topic_rows = []
    for topic in roadmap["topics"][:6]:
        total_in_topic = len(topic["problems"])
        solved_in_topic = sum(1 for item in topic["problems"] if _status_for(state, item["slug"]) == "solved")
        topic_rows.append((topic["id"], topic["name"], solved_in_topic, total_in_topic))
    table = Table(title="Roadmap start", box=box.ROUNDED, expand=True)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Topic", style="bold")
    table.add_column("Progress")
    table.add_column("Solved", justify="right")
    for topic_id, name, solved_in_topic, total_in_topic in topic_rows:
        table.add_row(str(topic_id), name, _progress_text(solved_in_topic, total_in_topic), f"{solved_in_topic}/{total_in_topic}")
    console.print(table)
    console.print("[dim]Commands: walnut topics  |  walnut list arrays-and-hashing  |  walnut random --ready[/]")
    return 0


def cmd_next(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    state = progress_mod.load_progress(root)
    refs = all_problem_refs(root)
    ref = _next_ref(refs, state)
    if not ref:
        print("all problems solved")
        return 0
    if (console := _console(flags)):
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold cyan")
        table.add_column()
        table.add_row("Next", f"#{ref.id} {ref.title}")
        table.add_row("Difficulty", ref.difficulty)
        table.add_row("Topic", ref.topic_name)
        table.add_row("Run", f"walnut pick {ref.id}")
        console.print(Panel(table, title="Next up", border_style="green"))
    else:
        print(f"Next: #{ref.id} {ref.title} ({ref.difficulty})")
        print(f"Run: walnut pick {ref.id}")
    return 0


def cmd_random(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    refs = all_problem_refs(root)
    if args.ready:
        refs = [ref for ref in refs if ref.seeded]
    if args.difficulty:
        refs = [ref for ref in refs if ref.difficulty.lower() == args.difficulty.lower()]
    if args.topic:
        topic = resolve_topic(load_roadmap(root), args.topic)
        refs = [ref for ref in refs if ref.topic_slug == topic["slug"]]
    if args.unsolved:
        state = progress_mod.load_progress(root)
        refs = [ref for ref in refs if _status_for(state, ref.slug) != "solved"]
    if not refs:
        print("no problems match those filters")
        return 2
    ref = random.choice(refs)
    if (console := _console(flags)):
        console.print(
            Panel(
                f"[bold]#{ref.id} {ref.title}[/]\n{ref.difficulty} · {ref.topic_name}\n{ref.leetcode_url}\n\n[dim]walnut pick {ref.id}[/]",
                title="Random pick",
                border_style="magenta",
            )
        )
    else:
        print(f"#{ref.id} {ref.title} ({ref.difficulty})")
        print(ref.leetcode_url)
    return 0


def cmd_daily(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    refs = all_problem_refs(root)
    rng = random.Random(progress_mod.today_local())
    ref = rng.choice(refs)
    if (console := _console(flags)):
        console.print(
            Panel(
                f"[bold]#{ref.id} {ref.title}[/]\n{ref.difficulty} · {ref.topic_name}\n{ref.leetcode_url}\n\n[dim]walnut pick {ref.id}[/]",
                title=f"Daily pick · {progress_mod.today_local()}",
                border_style="cyan",
            )
        )
    else:
        print(f"Daily: #{ref.id} {ref.title} ({ref.difficulty})")
        print(ref.leetcode_url)
    return 0


def cmd_version(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    print(__version__)
    return 0


def _load_scraped_metadata(source: str | None) -> list[neetcode.RoadmapProblem]:
    if source:
        path = Path(source)
        if path.exists():
            return neetcode.extract_neetcode_150(path.read_text(encoding="utf-8", errors="ignore"))
        if source.startswith("http"):
            import urllib.request

            with urllib.request.urlopen(source, timeout=30) as response:
                return neetcode.extract_neetcode_150(response.read().decode("utf-8", "ignore"))
        raise FileNotFoundError(source)
    return neetcode.fetch_neetcode_150()


def cmd_sync_roadmap(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    roadmap = load_roadmap(root)
    scraped = _load_scraped_metadata(args.source)
    diffs = neetcode.diff_roadmap_metadata(roadmap, scraped)
    if args.apply:
        changed = neetcode.apply_metadata(root, roadmap, scraped)
        message = f"synced {len(scraped)} NeetCode 150 metadata rows; applied {changed} field updates"
    else:
        message = f"scraped {len(scraped)} NeetCode 150 metadata rows; {len(diffs)} metadata differences"

    if flags["json"]:
        _print_json(
            {
                "scraped": len(scraped),
                "differences": diffs,
                "applied": bool(args.apply),
            }
        )
    else:
        print(message)
        for diff in diffs[:20]:
            print(
                f"  LC {diff['leetcode']} {diff['field']}: "
                f"{diff['local']!r} -> {diff['scraped']!r}"
            )
        if len(diffs) > 20:
            print(f"  ... {len(diffs) - 20} more")
        if not args.apply:
            print("Run with --apply to update roadmap/problem metadata only.")
            if any(diff["field"] == "topic" for diff in diffs):
                print("Topic differences are report-only; --apply does not move folders yet.")
    return 0


def cmd_open_official(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    ref = resolve_problem(root, args.id)
    problem = load_problem(root, ref)
    if args.site == "neetcode":
        url = problem.get("neetcode_url") or "https://neetcode.io/roadmap"
    else:
        url = problem.get("leetcode_url") or ref.leetcode_url
    if args.print_url:
        print(url)
        return 0
    ok = webbrowser.open(url)
    if not ok:
        print(url)
    return 0


CHEAT_ALIASES = {
    "python": "python-stdlib",
    "stdlib": "python-stdlib",
    "complexity": "complexity",
    "big-o": "complexity",
    "bigo": "complexity",
}


def _resolve_cheatsheet(root: Path, token: str | None) -> Path | None:
    """Map a token (topic id/slug/name, problem id, or alias) to a sheet path."""
    if token is None:
        state = progress_mod.load_progress(root)
        active = state.get("active")
        if not active:
            return None
        ref = resolve_problem(root, active["slug"])
        return cheatsheet_path(root, ref.topic_slug)

    text = token.strip().lower()
    if text in CHEAT_ALIASES:
        return cheatsheet_path(root, CHEAT_ALIASES[text])
    if text.isdigit():
        ref = resolve_problem(root, text)
        return cheatsheet_path(root, ref.topic_slug)
    try:
        topic = resolve_topic(load_roadmap(root), text)
        return cheatsheet_path(root, topic["slug"])
    except KeyError:
        ref = resolve_problem(root, text)
        return cheatsheet_path(root, ref.topic_slug)


def cmd_cheat(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    sheets = cheatsheet_path(root, "python-stdlib").parent
    if args.list or (args.topic is None and _resolve_cheatsheet(root, None) is None):
        names = sorted(path.stem for path in sheets.glob("*.md"))
        if flags["json"]:
            _print_json(names)
        else:
            print("cheat sheets (walnut cheat <name|topic|problem id>):")
            for name in names:
                print(f"  {name}")
            print("no active problem; pick one or pass a topic")
        return 0
    path = _resolve_cheatsheet(root, args.topic)
    if path is None or not path.exists():
        print(f"no cheat sheet found{f' for {args.topic!r}' if args.topic else ''}")
        print("try: walnut cheat --list")
        return 2
    text = path.read_text(encoding="utf-8")
    if flags["json"]:
        _print_json({"sheet": path.stem, "path": str(path), "content": text})
    elif (console := _console(flags)):
        from rich.markdown import Markdown

        console.print(Markdown(text))
    else:
        print(text)
    return 0


def cmd_stop(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    state = progress_mod.load_progress(root)
    active = state.get("active")
    if not active:
        print("no active timer")
        return 0
    elapsed = int(time.time() - float(active.get("started_at", time.time())))
    state["active"] = None
    progress_mod.save_progress(root, state)
    print(f"stopped timer for {active.get('slug')} at {_format_time(elapsed)}")
    print("solution file and progress are untouched; pick again to restart the clock")
    return 0


def cmd_tui(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    from .tui import run_tui

    return run_tui(root)


def cmd_notes(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    ref = resolve_problem(root, args.id)
    notes = ensure_notes(root, ref)
    if args.open:
        _launch_editor(notes)
    else:
        print(notes)
    return 0


def cmd_selected(args: argparse.Namespace, flags: dict[str, bool]) -> int:
    root = _root_or_exit()
    interval = max(float(args.poll), 0.1)
    decode_errors = 0

    while True:
        try:
            selected = progress_mod.load_selected(root)
            slug = selected.get("slug")
            if not slug:
                active = progress_mod.load_progress(root).get("active") or {}
                slug = active.get("slug")
            decode_errors = 0
        except json.JSONDecodeError as exc:
            decode_errors += 1
            if decode_errors > 1 or not args.wait:
                print(f"error: selected state is not valid JSON: {exc}", file=sys.stderr)
                return 3
            time.sleep(interval)
            continue

        if slug:
            ref = resolve_problem(root, slug)
            if args.target == "slug":
                print(ref.slug)
            elif args.target == "dir":
                print(problem_dir(root, ref))
            elif args.target == "notes":
                print(ensure_notes(root, ref))
            else:
                print(ensure_solution(root, ref))
            return 0

        if not args.wait:
            print("no selected problem; highlight one in walnut tui or start one with walnut pick", file=sys.stderr)
            return 1

        time.sleep(interval)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="walnut")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("doctor").set_defaults(func=cmd_doctor)
    sub.add_parser("topics").set_defaults(func=cmd_topics)

    list_p = sub.add_parser("list")
    list_p.add_argument("topic", nargs="?")
    list_p.add_argument("--difficulty")
    list_p.add_argument("--status", choices=["unsolved", "attempted", "solved"])
    list_p.add_argument("--ready", action="store_true")
    list_p.set_defaults(func=cmd_list)

    show = sub.add_parser("show")
    show.add_argument("id")
    show.set_defaults(func=cmd_show)

    pick = sub.add_parser("pick")
    pick.add_argument("id")
    pick.add_argument("--open", action="store_true")
    pick.add_argument("--force", action="store_true")
    pick.set_defaults(func=cmd_pick)

    open_p = sub.add_parser("open")
    open_p.add_argument("id")
    open_p.add_argument("--force", action="store_true")
    open_p.set_defaults(func=cmd_open)
    edit = sub.add_parser("edit")
    edit.add_argument("id")
    edit.add_argument("--force", action="store_true")
    edit.set_defaults(func=cmd_open)

    test = sub.add_parser("test")
    test.add_argument("id")
    test.add_argument("--perf", action="store_true")
    test.set_defaults(func=cmd_test)

    run_p = sub.add_parser("run")
    run_p.add_argument("id")
    run_p.add_argument("--perf", action="store_true")
    run_p.set_defaults(func=cmd_run)

    hint = sub.add_parser("hint")
    hint.add_argument("id")
    hint.add_argument("n", type=int, nargs="?")
    hint.set_defaults(func=cmd_hint)

    solution = sub.add_parser("solution")
    solution.add_argument("id")
    solution.add_argument("-y", "--yes", action="store_true")
    solution.set_defaults(func=cmd_solution)

    reset = sub.add_parser("reset")
    reset.add_argument("id")
    reset.add_argument("--hard", action="store_true")
    reset.set_defaults(func=cmd_reset)

    verify = sub.add_parser("verify")
    target = verify.add_mutually_exclusive_group(required=True)
    target.add_argument("id", nargs="?")
    target.add_argument("--all", action="store_true")
    verify.set_defaults(func=cmd_verify)

    sub.add_parser("next").set_defaults(func=cmd_next)

    random_p = sub.add_parser("random")
    random_p.add_argument("--topic")
    random_p.add_argument("--difficulty")
    random_p.add_argument("--unsolved", action="store_true")
    random_p.add_argument("--ready", action="store_true")
    random_p.set_defaults(func=cmd_random)

    sub.add_parser("daily").set_defaults(func=cmd_daily)
    sub.add_parser("version").set_defaults(func=cmd_version)
    sub.add_parser("home").set_defaults(func=cmd_home)

    sync = sub.add_parser("sync-roadmap")
    sync.add_argument("--apply", action="store_true")
    sync.add_argument("--source", help="Optional local or URL JavaScript bundle to parse")
    sync.set_defaults(func=cmd_sync_roadmap)

    official = sub.add_parser("open-official")
    official.add_argument("id")
    official.add_argument("--site", choices=["leetcode", "neetcode"], default="leetcode")
    official.add_argument("--print", dest="print_url", action="store_true")
    official.set_defaults(func=cmd_open_official)

    sub.add_parser("stop").set_defaults(func=cmd_stop)

    sub.add_parser("tui").set_defaults(func=cmd_tui)

    cheat = sub.add_parser("cheat")
    cheat.add_argument("topic", nargs="?", help="topic id/slug/name, problem id, or python/complexity")
    cheat.add_argument("--list", action="store_true")
    cheat.set_defaults(func=cmd_cheat)

    notes = sub.add_parser("notes")
    notes.add_argument("id")
    notes.add_argument("--open", action="store_true")
    notes.set_defaults(func=cmd_notes)

    selected = sub.add_parser("selected")
    selected.add_argument("target", nargs="?", choices=["slug", "dir", "solution", "notes"], default="slug")
    selected.add_argument("--wait", action="store_true")
    selected.add_argument("--poll", type=float, default=0.5)
    selected.set_defaults(func=cmd_selected)

    return parser


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    raw, flags = _strip_global_flags(raw)
    if not raw:
        raw = ["home"] if flags["plain"] or flags["json"] or not sys.stdin.isatty() or not sys.stdout.isatty() else ["tui"]
    parser = build_parser()
    args = parser.parse_args(raw)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    try:
        return int(args.func(args, flags))
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        if flags.get("debug"):
            raise
        print(f"error: {exc}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
