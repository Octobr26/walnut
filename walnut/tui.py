from __future__ import annotations

import os
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any

from rich.text import Text

from .files import ensure_notes, ensure_solution
from .format import (
    STATUS_ICONS,
    failure_by_case as _failure_by_case,
    format_time as _format_time,
    progress_bar as _progress_bar,
    short as _short,
    status_for as _status_for,
    target_for as _target_for,
)
from . import progress as progress_mod
from .repo import (
    ProblemRef,
    all_problem_refs,
    cheatsheet_path,
    load_problem,
    load_roadmap,
    problem_dir,
)
from .runner import RunResult, run

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, VerticalScroll
    from textual.screen import ModalScreen
    from textual.widgets import Input, Markdown, OptionList, Static, TabbedContent, TabPane
    from textual.widgets.option_list import Option

    TEXTUAL_AVAILABLE = True
except Exception:  # pragma: no cover - import guard
    TEXTUAL_AVAILABLE = False


def _problem_row(ref: ProblemRef, status: str, width: int = 34) -> Text:
    icon, style = STATUS_ICONS.get(status, STATUS_ICONS["unsolved"])
    text = Text()
    text.append(f"{icon} ", style=style)
    text.append(f"{ref.id:>3}. ")
    title = ref.title if len(ref.title) <= width else ref.title[: width - 1] + "…"
    text.append(f"{title:<{width}} ")
    diff_style = {"Easy": "green", "Medium": "yellow", "Hard": "red"}.get(ref.difficulty, "white")
    text.append(ref.difficulty[0], style=diff_style)
    if not ref.seeded:
        text.append(" ·", style="dim")
    return text


if TEXTUAL_AVAILABLE:

    class CheatScreen(ModalScreen[None]):
        BINDINGS = [("escape", "dismiss", "Close"), ("q", "dismiss", "Close"), ("c", "dismiss", "Close")]

        def __init__(self, title: str, markdown: str) -> None:
            super().__init__()
            self._title = title
            self._markdown = markdown

        def compose(self) -> ComposeResult:
            with VerticalScroll(id="cheat-box"):
                yield Static(Text(self._title, style="bold cyan"), id="cheat-title")
                yield Markdown(self._markdown)

        def action_dismiss(self) -> None:
            self.dismiss(None)

    class WalnutApp(App[None]):
        TITLE = "walnut"
        CSS = """
        Screen { background: $surface; }
        #filter { display: none; dock: top; height: 3; margin: 0 1; }
        #filter.visible { display: block; }
        #body { height: 1fr; }
        #left { width: 44%; min-width: 40; background: $surface; }
        #detail-tabs { width: 1fr; border-left: solid $panel; background: $surface; }
        #detail-scroll, #test-scroll { padding: 1 2; background: $surface; }
        #status { dock: bottom; height: 2; padding: 0 1; background: $panel; border-top: solid $primary; }
        TabbedContent { height: 1fr; }
        TabPane { padding: 0 1 0 0; }
        OptionList { height: 1fr; border: none; background: transparent; }
        CheatScreen { align: center middle; }
        #cheat-box {
            width: 90%; height: 90%;
            background: $surface; border: round $accent; padding: 1 2;
        }
        """
        BINDINGS = [
            ("q", "quit", "Quit"),
            ("j", "cursor(1)", "Down"),
            ("k", "cursor(-1)", "Up"),
            ("[", "tab(-1)", "Previous tab"),
            ("]", "tab(1)", "Next tab"),
            ("s", "start", "Start"),
            ("e", "editor", "Editor"),
            ("t", "test", "Test"),
            ("r", "restart", "Reset"),
            ("n", "notes", "Notes"),
            ("c", "cheat", "Cheat sheet"),
            ("/", "filter", "Filter"),
            ("escape", "back", "Back"),
        ]

        def __init__(self, root: Path) -> None:
            super().__init__()
            self.root = root
            self.roadmap = load_roadmap(root)
            self.refs = all_problem_refs(root)
            self.by_slug = {ref.slug: ref for ref in self.refs}
            self.progress = progress_mod.load_progress(root)
            self._progress_stamp = self._progress_file_stamp()
            self._selected_slug: str | None = None
            self.drilled: str | None = None  # topic slug when inside a topic
            self.filter_text = ""
            self.test_outputs: dict[str, Text] = {}

        # ---------- data ----------

        def _progress_file_stamp(self) -> tuple[int, int]:
            path = progress_mod.progress_path(self.root)
            if not path.exists():
                return (0, 0)
            stat = path.stat()
            return (stat.st_mtime_ns, stat.st_size)

        def _reload_progress_if_changed(self) -> bool:
            stamp = self._progress_file_stamp()
            if stamp != self._progress_stamp:
                self._progress_stamp = stamp
                self.progress = progress_mod.load_progress(self.root)
                return True
            return False

        def _topic(self, slug: str) -> dict[str, Any]:
            return next(t for t in self.roadmap["topics"] if t["slug"] == slug)

        def _matches(self, ref: ProblemRef) -> bool:
            if not self.filter_text:
                return True
            needle = self.filter_text.lower()
            return needle in ref.title.lower() or needle in ref.slug or needle in str(ref.id)

        # ---------- layout ----------

        def compose(self) -> ComposeResult:
            yield Input(placeholder="filter (enter to apply, esc to clear)", id="filter")
            with Horizontal(id="body"):
                with TabbedContent(id="left"):
                    with TabPane("Topics", id="tab-topics"):
                        yield OptionList(id="topics-list")
                    with TabPane("All", id="tab-all"):
                        yield OptionList(id="all-list")
                with TabbedContent(id="detail-tabs"):
                    with TabPane("Problem", id="tab-problem"):
                        with VerticalScroll(id="detail-scroll"):
                            yield Static(id="detail")
                    with TabPane("Tests", id="tab-tests"):
                        with VerticalScroll(id="test-scroll"):
                            yield Static(id="test-detail")
            yield Static(id="status")

        def on_mount(self) -> None:
            self._populate_topics()
            self._populate_all()
            self._render_detail()
            self._render_tests()
            self._render_status()
            self.query_one("#topics-list", OptionList).focus()
            self.set_interval(1.0, self._tick)

        # ---------- list population ----------

        def _populate_topics(self) -> None:
            lst = self.query_one("#topics-list", OptionList)
            lst.clear_options()
            if self.drilled is None:
                for topic in self.roadmap["topics"]:
                    if self.filter_text and self.filter_text.lower() not in topic["name"].lower():
                        continue
                    total = len(topic["problems"])
                    solved = sum(
                        1 for p in topic["problems"] if _status_for(self.progress, p["slug"]) == "solved"
                    )
                    text = Text()
                    text.append(f"{topic['id']:>2}. {topic['name']:<28}")
                    style = "green" if solved == total else ("cyan" if solved else "dim")
                    text.append(f"{solved:>2}/{total}", style=style)
                    lst.add_option(Option(text, id=f"topic:{topic['slug']}"))
            else:
                for ref in self.refs:
                    if ref.topic_slug == self.drilled and self._matches(ref):
                        status = _status_for(self.progress, ref.slug)
                        lst.add_option(Option(_problem_row(ref, status), id=f"prob:{ref.slug}"))
            if lst.option_count:
                lst.highlighted = 0

        def _populate_all(self) -> None:
            lst = self.query_one("#all-list", OptionList)
            lst.clear_options()
            for ref in self.refs:
                if self._matches(ref):
                    status = _status_for(self.progress, ref.slug)
                    lst.add_option(Option(_problem_row(ref, status), id=f"prob:{ref.slug}"))
            if lst.option_count:
                lst.highlighted = 0

        def _refresh_lists(self, selected_slug: str | None = None) -> None:
            self._populate_topics()
            self._populate_all()
            if selected_slug is None:
                return
            for list_id in ("#topics-list", "#all-list"):
                lst = self.query_one(list_id, OptionList)
                for index in range(lst.option_count):
                    if lst.get_option_at_index(index).id == f"prob:{selected_slug}":
                        lst.highlighted = index
                        break

        # ---------- selection helpers ----------

        def _active_list(self) -> OptionList:
            tabs = self.query_one("#left", TabbedContent)
            list_id = "#topics-list" if tabs.active == "tab-topics" else "#all-list"
            return self.query_one(list_id, OptionList)

        def _highlighted_option(self) -> Option | None:
            lst = self._active_list()
            if lst.highlighted is None or not lst.option_count:
                return None
            return lst.get_option_at_index(lst.highlighted)

        def _highlighted_ref(self) -> ProblemRef | None:
            option = self._highlighted_option()
            if option is None or not option.id or not option.id.startswith("prob:"):
                return None
            return self.by_slug.get(option.id.split(":", 1)[1])

        # ---------- detail pane ----------

        def _render_detail(self) -> None:
            detail = self.query_one("#detail", Static)
            option = self._highlighted_option()
            if option is None or not option.id:
                detail.update("")
                self._render_tests()
                return
            kind, slug = option.id.split(":", 1)
            if kind == "topic":
                topic = self._topic(slug)
                total = len(topic["problems"])
                solved = sum(
                    1 for p in topic["problems"] if _status_for(self.progress, p["slug"]) == "solved"
                )
                text = Text()
                text.append(f"{topic['name']}\n\n", style="bold cyan")
                text.append(f"{solved}/{total} solved  ", style="bold")
                text.append(_progress_bar(solved, total, 18))
                text.append("\n\nProblems\n", style="bold")
                for item in topic["problems"][:10]:
                    ref = self.by_slug.get(item["slug"])
                    if ref is None:
                        continue
                    status = _status_for(self.progress, ref.slug)
                    icon, icon_style = STATUS_ICONS.get(status, STATUS_ICONS["unsolved"])
                    text.append(f"{icon} ", style=icon_style)
                    text.append(f"{ref.id:>3}. {ref.title}\n")
                if total > 10:
                    text.append(f"     {total - 10} more\n", style="dim")
                text.append("\nenter open  c cheat", style="dim")
                detail.update(text)
                self._render_tests()
                return

            ref = self.by_slug[slug]
            self._save_selected_once(ref.slug)
            problem = load_problem(self.root, ref)
            status = _status_for(self.progress, ref.slug)
            icon, style = STATUS_ICONS.get(status, STATUS_ICONS["unsolved"])
            text = Text()
            text.append(f"#{ref.id} {ref.title}\n", style="bold")
            diff_style = {"Easy": "green", "Medium": "yellow", "Hard": "red"}.get(ref.difficulty, "white")
            text.append(ref.difficulty, style=f"bold {diff_style}")
            text.append(f" · {ref.topic_name} · ", style="dim")
            text.append(f"{icon} {status}\n\n", style=style)
            text.append(problem.get("statement") or "Statement coming soon.")
            text.append("\n")
            for index, ex in enumerate(problem.get("examples") or [], start=1):
                text.append(f"\nExample {index}\n", style="bold cyan")
                text.append(f"  input:  {ex['input']}\n")
                text.append(f"  output: {ex['output']}\n")
                if ex.get("explanation"):
                    text.append(f"  {ex['explanation']}\n", style="dim")
            constraints = problem.get("constraints") or []
            if constraints:
                text.append("\nConstraints\n", style="bold magenta")
                for constraint in constraints:
                    text.append(f"  - {constraint}\n")
            text.append(f"\n{problem['leetcode_url']}\n", style="dim")
            if not problem.get("seeded"):
                text.append("\nNot seeded: no local tests yet.\n", style="yellow")
            detail.update(text)
            self._render_tests()
            self.query_one("#detail-scroll", VerticalScroll).scroll_home(animate=False)

        def _save_selected_once(self, slug: str) -> None:
            if slug == self._selected_slug:
                return
            progress_mod.save_selected(self.root, slug)
            self._selected_slug = slug

        def _render_tests(self) -> None:
            test_detail = self.query_one("#test-detail", Static)
            ref = self._highlighted_ref()
            if ref is None:
                test_detail.update(Text("Highlight a problem and press t to run its tests.", style="dim"))
                return

            output = self.test_outputs.get(ref.slug)
            if output is not None:
                test_detail.update(output)
                return

            text = Text()
            text.append(f"#{ref.id} {ref.title}\n", style="bold")
            text.append("No test run yet.\n\n", style="dim")
            if ref.seeded:
                text.append("Press t to run local tests for this problem.", style="dim")
            else:
                text.append("Not seeded: local tests are unavailable.", style="yellow")
            test_detail.update(text)

        def _format_test_result(self, ref: ProblemRef, problem: dict[str, Any], result: RunResult) -> Text:
            failures = _failure_by_case(result)
            text = Text()
            text.append(f"#{ref.id} {ref.title}\n", style="bold")
            text.append(f"{ref.difficulty} · {ref.topic_name}\n", style="dim")
            status = "PASS" if result.ok else "NEEDS WORK"
            text.append(f"\n{status}  {result.passed}/{result.total} cases\n", style="bold green" if result.ok else "bold red")

            if result.elapsed_by_case:
                text.append("\nCases\n", style="bold cyan")
                for item in result.elapsed_by_case:
                    failure = failures.get(item["index"])
                    ok = failure is None
                    text.append("  PASS" if ok else "  FAIL", style="green" if ok else "red")
                    note = f" ({item['note']})" if item.get("note") else ""
                    text.append(
                        f" case {item['index']} [{item['kind']}]{note} "
                        f"{item['elapsed']:.3f}s/{item['timeout_sec']:g}s\n"
                    )
            elif result.failures:
                text.append("\nImport failed before cases could run.\n", style="red")

            if result.failures:
                text.append("\nFailures\n", style="bold red")
                for failure in result.failures[:5]:
                    text.append(f"\ncase {failure.index}: {failure.kind}\n", style="bold")
                    if failure.note:
                        text.append(f"  note      {failure.note}\n")
                    if failure.args is not None:
                        text.append(f"  input     {_short(failure.args)}\n")
                    if failure.expected is not None:
                        text.append(f"  expected  {_short(failure.expected)}\n")
                    if failure.got is not None:
                        text.append(f"  got       {_short(failure.got)}\n")
                    if failure.error:
                        text.append(f"  error     {failure.error}\n", style="red")
                if len(result.failures) > 5:
                    text.append(f"\n{len(result.failures) - 5} more failures omitted.\n", style="dim")

            if result.slowest_case_sec is not None:
                text.append(f"\nslowest case: {result.slowest_case_sec:.3f}s\n", style="dim")
            if not problem.get("seeded"):
                text.append("\nNot seeded: local tests are unavailable.\n", style="yellow")
            return text

        # ---------- status bar ----------

        def _render_status(self) -> None:
            status = self.query_one("#status", Static)
            line1 = Text()
            active = self.progress.get("active")
            if active:
                slug = active.get("slug") or ""
                ref = self.by_slug.get(slug)
                started = float(active.get("started_at", time.time()))
                elapsed = int(time.time() - started)
                target = int(
                    active.get("target_sec")
                    or progress_mod.TARGET_TIMES.get(ref.difficulty if ref else "Medium", 1800)
                )
                over = elapsed > target
                line1.append("active ", style="bold cyan")
                line1.append(f"#{ref.id} {ref.title}" if ref else (slug or "--"))
                line1.append("  ⏱ ")
                line1.append(
                    f"{_format_time(elapsed)}/{_format_time(target)}",
                    style="red" if over else "green",
                )
                history = self.progress.get("problems", {}).get(slug, {}).get("history", [])
                if history:
                    last = history[-1]
                    ok = last.get("result") == "pass"
                    line1.append("  last test ")
                    line1.append(
                        f"{'✓' if ok else '✗'} {last.get('cases_passed')}/{last.get('cases_total')}",
                        style="green" if ok else "red",
                    )
            else:
                line1.append("no active problem", style="dim")
                line1.append("  (highlight one and press s)", style="dim")

            solved = sum(1 for ref in self.refs if _status_for(self.progress, ref.slug) == "solved")
            total = len(self.refs)
            line2 = Text()
            line2.append(f"{solved}/{total} solved ", style="bold")
            line2.append(_progress_bar(solved, total))
            streak = progress_mod.current_streak(self.progress)
            line2.append(f"  streak {streak}d", style="magenta")
            line2.append(
                "   s start  e editor  n notes  t test  r reset  [ ] tabs  c cheat  / filter  esc back  q quit",
                style="dim",
            )
            status.update(Text("\n").join([line1, line2]))

        def _tick(self) -> None:
            if self._reload_progress_if_changed():
                self._refresh_lists()
                self._render_detail()
            self._render_status()

        # ---------- events ----------

        def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
            self._render_detail()

        def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
            if event.option.id and event.option.id.startswith("topic:"):
                self.drilled = event.option.id.split(":", 1)[1]
                self.filter_text = ""
                self._populate_topics()
                self._render_detail()

        def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
            self._render_detail()

        def on_input_changed(self, event: Input.Changed) -> None:
            self.filter_text = event.value.strip()
            self._refresh_lists()
            self._render_detail()

        def on_input_submitted(self, event: Input.Submitted) -> None:
            self._active_list().focus()

        # ---------- actions ----------

        def action_cursor(self, delta: int) -> None:
            if isinstance(self.focused, OptionList):
                if delta > 0:
                    self.focused.action_cursor_down()
                else:
                    self.focused.action_cursor_up()

        def action_tab(self, delta: int) -> None:
            tabs = self.query_one("#left", TabbedContent)
            tab_ids = ("tab-topics", "tab-all")
            try:
                index = tab_ids.index(tabs.active)
            except ValueError:
                index = 0
            tabs.active = tab_ids[(index + delta) % len(tab_ids)]
            self._active_list().focus()

        def action_back(self) -> None:
            filter_input = self.query_one("#filter", Input)
            if filter_input.has_focus or self.filter_text:
                filter_input.value = ""
                self.filter_text = ""
                filter_input.remove_class("visible")
                self._refresh_lists()
                self._active_list().focus()
                return
            detail_tabs = self.query_one("#detail-tabs", TabbedContent)
            if detail_tabs.active == "tab-tests":
                self._select_detail_tab("tab-problem")
                self._active_list().focus()
                return
            if self.drilled is not None:
                previous = self.drilled
                self.drilled = None
                self._populate_topics()
                lst = self.query_one("#topics-list", OptionList)
                for index in range(lst.option_count):
                    if lst.get_option_at_index(index).id == f"topic:{previous}":
                        lst.highlighted = index
                        break
                self._render_detail()

        def action_filter(self) -> None:
            filter_input = self.query_one("#filter", Input)
            filter_input.add_class("visible")
            filter_input.focus()

        def _select_detail_tab(self, tab_id: str) -> None:
            self.query_one("#detail-tabs", TabbedContent).active = tab_id

        def _tmux_session(self) -> str | None:
            if not os.environ.get("TMUX"):
                return None
            if session := os.environ.get("WALNUT_TMUX_SESSION"):
                return session
            completed = subprocess.run(
                ["tmux", "display-message", "-p", "#S"],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                return None
            return completed.stdout.strip() or None

        def _open_nvim_window(self, window_name: str, path: Path) -> None:
            session = self._tmux_session()
            if session is None:
                self.notify(f"{window_name}: {path}", timeout=8)
                return

            window_env = f"WALNUT_TMUX_{window_name.upper()}_WINDOW"
            window = os.environ.get(window_env, window_name)
            target = f"{session}:{window}"
            current = subprocess.run(
                ["tmux", "display-message", "-p", "-t", target, "#{pane_current_command}"],
                capture_output=True,
                text=True,
                check=False,
            )
            if current.returncode != 0:
                self.notify(f"tmux window not found: {target}", severity="warning")
                return

            pane_command = current.stdout.strip()
            if pane_command in {"nvim", "vim", "vi"}:
                vim_path = str(path).replace("\\", "\\\\").replace(" ", "\\ ")
                send = ["tmux", "send-keys", "-t", target, "Escape", f":edit {vim_path}", "C-m"]
            else:
                command = f"nvim {shlex.quote(str(path))}"
                send = ["tmux", "send-keys", "-t", target, "C-c", command, "C-m"]

            sent = subprocess.run(send, capture_output=True, text=True, check=False)
            if sent.returncode != 0:
                self.notify(f"could not open {path}", severity="warning")
                return
            subprocess.run(["tmux", "select-window", "-t", target], check=False)

        def action_start(self) -> None:
            ref = self._highlighted_ref()
            if ref is None:
                self.notify("highlight a problem first", severity="warning")
                return
            problem = load_problem(self.root, ref)
            ok, active_slug, state, solution, existed = progress_mod.start_problem(self.root, ref, problem=problem)
            if not ok:
                self.notify(f"timer already active for {active_slug} — finish or reset it first", severity="warning")
                return
            self.progress = state
            self._progress_stamp = self._progress_file_stamp()
            self._refresh_lists(ref.slug)
            self._render_status()
            verb = "ready" if existed else "created"
            self.notify(f"{verb}: {solution}\ntest: walnut test {ref.id} --perf", timeout=8)

        def action_editor(self) -> None:
            ref = self._highlighted_ref()
            if ref is None:
                self.notify("highlight a problem first", severity="warning")
                return
            problem = load_problem(self.root, ref)
            solution = ensure_solution(self.root, ref, problem)
            progress_mod.save_selected(self.root, ref.slug)
            self._open_nvim_window("editor", solution)

        def action_restart(self) -> None:
            state = progress_mod.load_progress(self.root)
            active = state.get("active")
            if not active:
                self.notify("no active timer to reset", severity="warning")
                return
            elapsed = int(time.time() - float(active.get("started_at", time.time())))
            state["active"] = None
            progress_mod.save_progress(self.root, state)
            self.progress = state
            self._progress_stamp = self._progress_file_stamp()
            self._render_status()
            self.notify(f"reset {active.get('slug')} at {_format_time(elapsed)}; press s to start again")

        def action_notes(self) -> None:
            ref = self._highlighted_ref()
            if ref is None:
                self.notify("highlight a problem first", severity="warning")
                return
            notes = ensure_notes(self.root, ref)
            progress_mod.save_selected(self.root, ref.slug)
            self._open_nvim_window("notes", notes)

        def action_test(self) -> None:
            ref = self._highlighted_ref()
            if ref is None:
                self.notify("highlight a problem first", severity="warning")
                return

            progress_mod.save_selected(self.root, ref.slug)
            self._select_detail_tab("tab-tests")
            test_detail = self.query_one("#test-detail", Static)
            running = Text()
            running.append(f"#{ref.id} {ref.title}\n", style="bold")
            running.append("Running tests...\n", style="yellow")
            test_detail.update(running)

            problem = load_problem(self.root, ref)
            if not problem.get("seeded"):
                output = Text()
                output.append(f"#{ref.id} {ref.title}\n", style="bold")
                output.append("Not seeded: local tests are unavailable.\n", style="yellow")
                self.test_outputs[ref.slug] = output
                test_detail.update(output)
                return

            self.run_worker(
                lambda: self._run_test_worker(ref),
                name=f"test-{ref.slug}",
                group="tests",
                exit_on_error=False,
                thread=True,
            )

        def _run_test_worker(self, ref: ProblemRef) -> None:
            problem = load_problem(self.root, ref)
            ensure_solution(self.root, ref, problem)
            result = run(problem_dir(self.root, ref), problem)
            output = self._format_test_result(ref, problem, result)
            state, _record, _elapsed = progress_mod.record_run(self.root, ref, problem, result)
            self.call_from_thread(self._finish_test_worker, ref.slug, output, state)

        def _finish_test_worker(self, slug: str, output: Text, state: dict[str, Any]) -> None:
            test_detail = self.query_one("#test-detail", Static)
            self.test_outputs[slug] = output
            test_detail.update(output)
            self.query_one("#test-scroll", VerticalScroll).scroll_home(animate=False)
            self.progress = state
            self._progress_stamp = self._progress_file_stamp()
            self._refresh_lists(slug)
            self._render_status()

        def action_cheat(self) -> None:
            ref = self._highlighted_ref()
            if ref is not None:
                slug = ref.topic_slug
            elif self.drilled is not None:
                slug = self.drilled
            else:
                option = self._highlighted_option()
                if option is not None and option.id and option.id.startswith("topic:"):
                    slug = option.id.split(":", 1)[1]
                else:
                    slug = "python-stdlib"
            path = cheatsheet_path(self.root, slug)
            if not path.exists():
                self.notify(f"no cheat sheet: {path.name}", severity="warning")
                return
            self.push_screen(CheatScreen(slug, path.read_text(encoding="utf-8")))


def run_tui(root: Path) -> int:
    if not TEXTUAL_AVAILABLE:
        print("walnut tui needs Textual. Run ./setup from the Walnut repo root, or pip install -e . inside the venv.")
        return 3
    WalnutApp(root).run()
    return 0
