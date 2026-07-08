# `walnut` — Offline NeetCode-150 Practice CLI
## Plan & Technical Design Document

**Status:** Draft, ready for implementation
**Author:** Luis
**Date:** 2026-07-01
**Target implementer:** Contributors
**Language:** Python 3.9+
**One-line pitch:** A git repo you clone on any machine, `pip install -e .`, and use entirely offline to grind the NeetCode 150 from your terminal — with a local test runner, hints, reference solutions, an interview timer, and diagnostic stats that tell you *what to improve*.

---

### How to use this document
This is a self-contained, implementation-ready spec. An agent should be able to build the whole tool from it without further questions. Sections are ordered so you can implement in phases (see **§20 Build Milestones**). Where a JSON example has to omit comments (JSON forbids them), the authoritative field definitions live in the accompanying field tables.

---

## Table of Contents

**Part I — Plan**
1. Summary
2. Goals & Non-Goals
3. Locked Decisions
4. Usage Scenarios
5. Terminal Experience Vision

**Part II — Technical Design**
6. High-Level Architecture
7. Repository Layout
8. Installation, Portability & Offline Behavior
9. Repo Discovery
10. Data Model & Schemas
11. Test Runner Contract
12. CLI Command Reference
13. Progress, Stats & the "What to Improve" Engine
14. Spaced Repetition
15. Timer / Interview Mode
16. Terminal Design System (rich)
17. Configuration
18. Error Handling & Exit Codes
19. Content Seeding Pipeline
20. Build Milestones
21. Testing & Verification
22. Risks & Mitigations
23. Resolved Decisions
24. Review Resolutions

**Part III — Appendices**
- A. Full NeetCode 150 list
- B. Example `problem.json` (Two Sum)
- C. `pyproject.toml`, `.gitignore`, starter/reference conventions
- D. Command cheat sheet
- E. Glossary, credits & legal note

---

# Part I — Plan

## 1. Summary

`walnut` is a terminal-first, fully-offline practice environment built around the **NeetCode 150** roadmap (18 topics, 150 problems, taught in dependency order). You clone the repo, install once, and then everything works with no network:

- Browse topics and problems, read a restated statement, and start coding.
- Your solution lives in the problem's own folder as `solution.py` (git-ignored, so it stays on your machine and never pollutes the repo).
- `walnut test <id>` runs your code against **local** test cases and reports pass/fail.
- Progressive **hints** and a **reference solution** are bundled for every seeded problem (since you can't watch NeetCode videos offline).
- An **interview timer** records how long you take; a **diagnostic stats** view tells you which patterns are slow, shaky, or overdue for review.
- Because your solutions and progress are git-ignored, re-cloning on any machine gives a pristine, fresh install.

## 2. Goals & Non-Goals

### Goals
- **Offline-first.** Zero network calls for any core workflow (browse, solve, test, stats, review). No login, no cookies, no API.
- **Portable & reproducible.** `git clone` + one install command works on macOS, Linux, and Windows.
- **Fresh installs.** The tracked repo contains only the "product" (problems, tooling, reference solutions). Personal artifacts (your `solution.py` files, your progress/stats) are git-ignored.
- **Learning-oriented.** Follows the NeetCode roadmap order; every seeded problem has restated statement, examples, constraints, progressive hints, local tests, and a reference solution.
- **Diagnostic.** Stats surface *what to improve* — weak patterns, slow solves, low first-try recall, overdue reviews — not just totals.
- **Fun to use.** Polished terminal UI (via `rich`): colored tables, boxed panels, syntax-highlighted solutions, sparklines, a streak heatmap.
- **Extensible.** Clear schema to seed more problems or (later) add more languages.

### Non-Goals
- **No submitting to LeetCode.** Impossible offline and out of scope.
- **No scraping of LeetCode/NeetCode content.** Statements are original restatements; we link out to the official problem.
- **No accounts, sync servers, or collaboration/rooms.** (The reference project's login/collab features are intentionally dropped — they require the network.)
- **No auto-grading against hidden/official test suites.** We ship our own cases.
- **v1 is Python-only.** Multi-language is designed-for but not built.

## 3. Locked Decisions

| # | Decision | Choice |
|---|----------|--------|
| 1 | Solve language (v1) | **Python 3.9+** |
| 2 | Problem set | **NeetCode 150**, mirrored structure & order |
| 3 | Distribution | **Git repo**, portable, installs fresh anywhere |
| 4 | Where solutions live | **In each problem's folder** as `solution.py`, **git-ignored** (kept locally so you can review your own code + solve times) |
| 5 | Progress/stats/timer logs | **Local only**, git-ignored in `.walnut/`; a fresh clone starts at zero |
| 6 | Install method | **`pip install -e .`** exposing a `walnut` command (cross-platform) |
| 7 | Hints & solutions | **Both included** — progressive hints + `walnut solution <id>` reference |
| 8 | Terminal UX | **Polished with `rich`** (single dependency): tables, panels, syntax highlighting, sparklines |
| 9 | Stats philosophy | **Diagnostic** — feature the signals that reveal what to improve |
| 10 | Statement content | **Original restatements** only; link to LeetCode for the official version |
| 11 | Per-case timeout | **Thread-based best-effort** — hard-stop via SIGALRM on mac/Linux, thread-future on Windows; generous per-case budgets |
| 12 | `rich` availability | **Rely on `pip`** at install; built-in plain-text fallback if `rich` is missing (no vendoring) |
| 13 | Solution snapshots | **Versioned snapshots** via `walnut snapshot` under `.walnut/snapshots/<slug>/` (compare brute-force vs optimized) |
| 14 | Progress portability | **Local only** — no export; a fresh clone starts at zero |
| 15 | Daily/random pool | **All 150** — unseeded picks show statement + link (no local tests yet) |
| 16 | Multi-language | **Reserve schema now, build Python-only** (see §23a) |
| 17 | Edge/perf testing | Tagged cases (`example`/`edge`/`stress`) + per-case timing & bottleneck reporting (see §11a) |

## 4. Usage Scenarios

**A. Daily offline grind (on a plane / no wifi).**
`walnut daily` → read the problem → `walnut pick <id>` (creates `solution.py`, starts the timer) → edit in your terminal editor → `walnut test <id>` → passes → "Solved in 7:42, new best." Progress + time saved locally.

**B. Interview simulation.**
`walnut timer <id> --minutes 30 --watch` runs a live countdown in one pane while you solve in another. On pass, `walnut` reports whether you beat the target.

**C. Targeted improvement.**
`walnut stats` shows a dashboard; the **Focus Areas** panel says e.g. "Sliding Window: 40% first-try, avg 1.8× target time — weakest pattern." `walnut focus` then hands you the next problem to drill in that pattern.

**D. Spaced review.**
`walnut review` lists problems due today (previously solved, resurfacing on an expanding schedule, plus anything you lapsed on). Re-solve to reinforce.

**E. Fresh machine.**
`git clone … && cd … && pip install -e . && walnut doctor` → ready. No personal data carried over (by design).

## 5. Terminal Experience Vision

- Running `walnut` (no args) or `walnut home` shows a compact dashboard: today's daily problem, current streak, "N reviews due", "next unsolved: …", and a one-line nudge.
- Consistent **color language**: Easy = green, Medium = amber, Hard = red; success = green, failure = red, review = magenta, accent = cyan, muted = grey.
- **Panels** for reading a problem; **tables** for lists; **syntax-highlighted** code for reference solutions and failing-case diffs; **sparklines** and a **heatmap** for stats.
- Everything degrades gracefully to plain text when piped, when `NO_COLOR` is set, or with `--plain`.

---

# Part II — Technical Design

## 6. High-Level Architecture

A single installable Python package `walnut` plus a data tree in the repo root.

```
┌──────────────────────────────────────────────────────────┐
│  walnut (console entry point)  ->  walnut.cli:main          │
├──────────────────────────────────────────────────────────┤
│  cli.py        argument parsing + command dispatch          │
│  repo.py       repo discovery, roadmap/problem loading      │
│  runner.py     import solution.py, run cases, compare       │
│  progress.py   read/write .walnut/progress.json, metrics      │
│  stats.py      aggregation + "what to improve" scoring      │
│  review.py     spaced-repetition scheduling                 │
│  timer.py      interview timer / countdown                  │
│  ui.py         rich rendering helpers (tables/panels/…)     │
│  seed.py       problem.json validation, README generation   │
└──────────────────────────────────────────────────────────┘
        │ reads/writes
        ▼
repo/roadmap.json          (index of all 150)
repo/problems/**/problem.json, starter.py, reference.py, README.md   (tracked)
repo/problems/**/solution.py                                          (git-ignored)
repo/.walnut/progress.json, config.json                                 (git-ignored)
```

Module split is a recommendation; a smaller build may consolidate `stats/review/timer` into `progress.py`. Only external dependency is **`rich`**.

## 7. Repository Layout

```
walnut/
├── pyproject.toml                 # packaging + `walnut` entry point            (tracked)
├── README.md                      # what it is, install, quickstart, legal    (tracked)
├── .gitignore                     # ignores solution.py, .walnut/, caches        (tracked)
├── walnut                           # optional shim to run ./walnut pre-install    (tracked)
├── roadmap.json                   # index of all 150 problems + metadata       (tracked)
├── walnut/                       # the CLI package                            (tracked)
│   ├── __init__.py
│   ├── cli.py
│   ├── repo.py
│   ├── runner.py
│   ├── progress.py
│   ├── stats.py
│   ├── review.py
│   ├── timer.py
│   ├── ui.py
│   └── seed.py
├── problems/
│   ├── 01-arrays-and-hashing/
│   │   ├── 01-contains-duplicate/
│   │   │   ├── problem.json        # machine source of truth                   (tracked)
│   │   │   ├── README.md            # human view, generated from problem.json   (tracked)
│   │   │   ├── starter.py           # empty template w/ correct signature       (tracked)
│   │   │   ├── reference.py          # worked solution (shown via walnut solution) (tracked)
│   │   │   └── solution.py           # YOUR attempt (created by walnut pick)   (GIT-IGNORED)
│   │   ├── 02-valid-anagram/…
│   │   └── … (9 problems)
│   ├── 02-two-pointers/…            # (5 problems)
│   └── … 18 topic folders, 150 problems total
├── _template/                      # copy-me skeleton for seeding new problems  (tracked)
│   ├── problem.json
│   ├── starter.py
│   └── reference.py
├── tests/                          # unit tests for runner/compare/progress     (tracked)
└── .walnut/                          # created on first run                    (GIT-IGNORED)
    ├── progress.json
    ├── config.json
    └── snapshots/<slug>/…           # named solution snapshots (walnut snapshot)
```

**Tracked vs ignored** — the crux of "installs fresh, doesn't track my submissions":

| Path | Tracked? | Why |
|------|----------|-----|
| `walnut/`, `pyproject.toml`, `roadmap.json`, `problems/**/{problem.json,README.md,starter.py,reference.py}`, `_template/`, `tests/` | ✅ tracked | The product |
| `problems/**/solution.py` | 🚫 ignored | Your attempts — kept locally, never committed |
| `.walnut/` | 🚫 ignored | Your progress, stats, timers, config |
| `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`, `.DS_Store` | 🚫 ignored | Noise |

Naming guarantees no clash: `starter.py`/`reference.py` are tracked, `solution.py` is the only ignored code file, so `**/solution.py` in `.gitignore` never masks tracked content.

## 8. Installation, Portability & Offline Behavior

**Install (one time per machine, needs network once to fetch `rich`):**
```bash
git clone <your-repo-url> walnut
cd walnut
python -m pip install -e .        # installs `rich`, exposes `walnut`
walnut doctor                        # verifies environment, prints repo path
```

- **`pip install -e .` (editable)** keeps the package inside the cloned repo, so the tool can always find `problems/` and `roadmap.json` relative to itself (see §9).
- **Offline use:** after install, no command touches the network. **Decision:** rely on `pip` to fetch `rich` at install time; if `rich` is ever missing (e.g. a locked-down offline box), the CLI falls back to a built-in plain-text renderer so every command still works, just less pretty. We do **not** vendor `rich`.
- **Cross-platform:** pure-Python; the only OS-specific concern is the per-case execution timeout (see §11).
- **No install fallback:** `./walnut <cmd>` shim inserts the repo root on `sys.path` and calls `walnut.cli:main`, for users who don't want to install.

## 9. Repo Discovery

`repo.find_root()` resolves the repo root in this order:
1. `$WALNUT_HOME` env var, if set and contains `roadmap.json`.
2. Walk **upward from the current working directory**; first ancestor containing `roadmap.json` wins (lets you run `walnut` from any subfolder).
3. **Package-relative:** `Path(walnut.__file__).resolve().parents[1]` (works for editable installs, where the package lives in the repo).
4. Else exit code 3 with a helpful message ("run inside the repo or set `WALNUT_HOME`").

## 10. Data Model & Schemas

Three JSON shapes. All timestamps are epoch seconds (float); all dates are `YYYY-MM-DD` (local time).

### 10.1 `roadmap.json` (the index)

| Field | Type | Notes |
|-------|------|-------|
| `version` | int | Schema version (start at 1) |
| `language` | string | `"python"` |
| `source` | string | `"NeetCode 150"` |
| `topics[]` | array | 18 topics, in roadmap order |
| `topics[].id` | int | 1–18 |
| `topics[].slug` | string | e.g. `arrays-and-hashing` |
| `topics[].name` | string | e.g. `Arrays & Hashing` |
| `topics[].blurb` | string | one-line "why this pattern matters" |
| `topics[].problems[]` | array | in intended order |
| `…problems[].id` | int | **global** 1–150 |
| `…problems[].slug` | string | kebab-case |
| `…problems[].title` | string | display title |
| `…problems[].difficulty` | enum | `Easy`\|`Medium`\|`Hard` |
| `…problems[].leetcode` | int | LeetCode problem number |
| `…problems[].leetcode_url` | string | canonical URL |
| `…problems[].method` | string\|null | primary `Solution` method (null for design problems) |
| `…problems[].seeded` | bool | are local tests + reference present? |
| `…problems[].dir` | string | repo-relative folder path |

### 10.2 `problem.json` (per-problem source of truth)

| Field | Type | Notes |
|-------|------|-------|
| `id`,`slug`,`title`,`difficulty` | — | mirror roadmap |
| `topic`,`topic_slug` | string | denormalized for convenience |
| `leetcode`,`leetcode_url` | — | official problem link |
| `neetcode_url` | string\|null | optional deep link; else null (README links the roadmap) |
| `pattern` | string | short technique tag (e.g. "Hash map complement lookup") |
| `seeded` | bool | true when tests+reference exist |
| `runner` | object | how to execute (see below) |
| `runner.entry` | enum | `method`\|`roundtrip`\|`design`\|`checker` |
| `runner.method` | string | method name for `method` entry |
| `runner.encode`/`decode` | string | method names for `roundtrip` entry |
| `runner.class` | string | class name for `design` entry (e.g. `MinStack`) |
| `runner.compare` | enum | `exact`\|`sorted`\|`groups`\|`approx`\|`bool` |
| `runner.timeout_sec` | number | per-case timeout budget; generous by default (10s), raise for heavy problems |
| `statement` | string (markdown) | **original** restatement |
| `examples[]` | array | `{input, output, explanation?}` display strings |
| `constraints[]` | string[] | display strings |
| `hints[]` | string[] | progressive, revealed one at a time |
| `cases[]` | array | test cases; shape depends on `runner.entry` (see §11) |
| `cases[].kind` | enum? | `example`\|`edge`\|`stress`; **optional, defaults to `example`** — drives labeling and failure attribution (missed edge vs. too slow) |
| `cases[].timeout_sec` | number? | optional per-case override; `stress` cases may get a larger budget |
| `cases[].note` | string? | optional label shown on failure (e.g. "empty input", "n=10^5") |
| `cases[].gen` | object? | optional generator for large `stress` cases: `{fn, seed}` → `fixtures.py::<fn>(seed)` returns `{args, expected}`; if absent, inline `args`/`expected` are used |

### 10.3 `.walnut/progress.json`

| Field | Type | Notes |
|-------|------|-------|
| `version` | int | schema version |
| `active` | object\|null | `{slug, started_at, target_sec?}` — the currently-timed attempt |
| `problems{slug}` | map | per-problem record (below) |
| `streak` | object | `{current, longest, last_solved_date, active_days[]}` |

Per-problem record:

| Field | Type | Meaning |
|-------|------|---------|
| `status` | enum | `unsolved`\|`attempted`\|`solved` |
| `attempts` | int | failed `test` runs before first pass, +1 |
| `test_runs` | int | total `walnut test` invocations |
| `revealed_hints` | int | how many hints shown |
| `revealed_solution` | bool | did you open the reference before solving? |
| `first_seen_at` | float | first `pick`/`open` |
| `solved_at` | float\|null | first pass timestamp |
| `first_try` | bool | passed on first `test`, no hints, no reference |
| `best_time_sec` | int\|null | fastest timed solve |
| `last_time_sec` | int\|null | most recent timed solve |
| `history[]` | array | `{at, time_sec?, result, cases_passed, cases_total}` |
| `review` | object | `{due, interval_days, ease, reps, lapses}` (see §14) |
| `snapshots[]` | array | `{name, at, note?}` — versioned saves under `.walnut/snapshots/<slug>/` (see §12) |
| `slowest_case_sec` | float\|null | slowest case time on the last run — surfaced as a bottleneck signal |

## 11. Test Runner Contract

`runner.run(problem_dir, problem_json) -> RunResult`. Steps:

1. **Locate the target module** — `solution.py` by default, or `reference.py` when invoked by `walnut verify` (the runner accepts a `module_filename` parameter). If a required `solution.py` is missing → guide the user to `walnut pick`.
2. **Import** it via `importlib.util.spec_from_file_location` under a throwaway module name. Catch `SyntaxError`/import-time exceptions and surface them as a failed run (show the traceback's last frames).
3. **Resolve entry point** from `runner.entry`:
   - **`method`** (default): instantiate `Solution()`, call `getattr(sol, runner.method)(**deepcopy(case.args))`.
   - **`roundtrip`**: `dec = sol.<decode>(sol.<encode>(**deepcopy(case.args)))`; compare `dec` to `case.expected` (which equals the original input list). Used by Encode/Decode Strings.
   - **`design`** *(future topics)*: LeetCode-style parallel arrays — `case = {"ops": ["ClassName", "push", "pop", …], "args": [[ctorArgs…], [1], [], …], "expected": [null, null, 1, …]}`, all three equal length. `ops[0]` constructs the class named by `runner.class` (with `expected[0] = null`); each later op calls that method and its return is compared (use `null` for void methods).
   - **`checker`** *(optional)*: for problems with multiple valid answers, a `checker.py` in the dir exposes `check(args, output) -> bool`; the runner calls it instead of value comparison. Checker cases omit `expected` (shape `{"kind"?, "args": {…}}`); a truthy return is a pass.
4. **Deep-copy inputs** before every call (many solutions mutate inputs; e.g. `3Sum` sorts). Never share args across cases.
5. **Timeout** each case at `cases[].timeout_sec` (else `runner.timeout_sec`, generous by default). **Decision: thread-based best-effort.**
   - **Unix (mac/Linux):** `signal.setitimer(ITIMER_REAL, t)` + `SIGALRM` handler raising `TimeoutError` (runner runs in the main thread). A real hard-stop, even for CPU-bound loops.
   - **Windows / no SIGALRM:** run the call in a `concurrent.futures.ThreadPoolExecutor` with `future.result(timeout=t)`. The case is reported as timed out and the CLI continues to the next case; a non-returning worker thread keeps running in the background until the process exits (accepted trade-off — see §22).
   - Budgets are generous so a correct optimal solution always passes; only wrong-complexity solutions trip them — which is exactly the bottleneck signal (see §11a).
6. **Compare** `got` vs `expected` using `runner.compare`:
   - `exact` → `got == expected`
   - `bool` → `bool(got) == bool(expected)`
   - `sorted` → `sorted(got) == sorted(expected)` (order-independent flat list; e.g. Two Sum indices, Top K Frequent)
   - `groups` → `normalize(x) == normalize(y)` where `normalize = sorted([sorted(g) for g in x])` (list-of-lists, both levels order-independent; e.g. Group Anagrams, 3Sum)
   - `approx` → element-wise `abs(a-b) <= 1e-6` (floating point)
7. **Return** `RunResult{passed:int, total:int, failures:[{index, kind, note, args, expected, got|error}], elapsed_by_case, slowest_case_sec}`. Each failure carries its `kind` so the UI can say "passed examples, failed the stress case (too slow)".

**`RunResult` → progress side effects** happen in the command layer (§12 `test`), not the runner, so the runner stays pure/testable.

### 11a. Edge cases, stress cases & bottleneck feedback
Interviews test whether you cover edge cases **and** hit the right complexity, so the runner treats both as first-class:
- **Case kinds.** Every seeded problem ships `example` cases (from the statement), `edge` cases (empty, single element, duplicates, negatives, min/max values, overflow-ish inputs), and at least one `stress` case (large input, e.g. n=10⁴–10⁵) where a naive/brute-force complexity can't finish inside the budget.
- **Failure attribution.** `walnut test` labels each case by kind. Passing every `example`/`edge` but failing a `stress` case = correct logic, wrong complexity (the classic bottleneck). Failing an `edge` case = a missed corner case.
- **Timing report.** The runner records per-case wall-clock time and reports the slowest case (e.g. "slowest: stress, 1.8s / 10s budget"), so you see how close you are to the limit even when green. `walnut test --perf` prints timing for every case.
- **Stress budgets.** `stress` cases can set a larger `cases[].timeout_sec`; that budget is the efficiency bar you must beat — a Python-idiomatic optimal solution should clear it comfortably.

## 12. CLI Command Reference

Global conventions: `<id>` accepts a **global id (1–150)**, a **slug**, or an unambiguous slug prefix. Flags: `--plain` (no color/box), `--json` (machine output where sensible), `-h/--help`. Exit codes in §18.

| Command | Synopsis | Behavior |
|---------|----------|----------|
| `walnut` / `walnut home` | dashboard | Daily problem, streak, reviews due, next unsolved, nudge line. |
| `walnut doctor` | env check | Python version, `rich` availability, repo path, counts of seeded/total, writable `.walnut/`. |
| `walnut topics` | list topics | 18 rows: number, name, `solved/total` with a progress bar, `ready` (seeded) count. |
| `walnut list [topic] [--difficulty D] [--status S] [--ready] [--due]` | list problems | Table: id, status glyph, title, difficulty (colored), topic, tags (`no local tests`, `review due`). Filters combine. |
| `walnut show <id>` | read problem | Panel: header (`#3 · Two Sum · Easy · Arrays & Hashing`), statement, examples, constraints, links, footer of commands. Hints hidden. |
| `walnut pick <id> [--open]` | start solving | Copies `starter.py`→`solution.py` if absent (never overwrites); sets `active={slug,started_at=now}`; marks `attempted`; prints path + tip; `--open` launches `$EDITOR`. |
| `walnut open <id>` / `walnut edit <id>` | edit | Ensures `solution.py` exists, opens it in the configured editor; arms timer if not armed. |
| `walnut test <id> [--perf]` | run tests | Runs the runner; prints per-case ✓/✗ labeled by kind (example/edge/stress); on any fail shows Input/Expected/Got (+ "timed out" for too-slow cases). Reports the slowest case as a bottleneck signal; `--perf` shows timing for every case. On all-pass: records time (if armed), sets `solved`, updates `best/last`, `first_try`, streak, schedules review; prints success panel + time + streak. On fail: `attempts++`, `test_runs++`. |
| `walnut run <id>` | quick run | Like `test` but does **not** mutate progress (dry run / debugging). |
| `walnut hint <id> [n]` | reveal hint | Shows hint `n` (default: next unrevealed). Increments `revealed_hints`. |
| `walnut solution <id> [-y]` | reference | Prints `reference.py` syntax-highlighted after a confirm (skip with `-y`). Sets `revealed_solution=true` (affects `first_try`). |
| `walnut next` | next problem | First unsolved in roadmap order (prefers seeded). Shows it + suggests `pick`. |
| `walnut random [--topic T] [--difficulty D] [--unsolved] [--ready]` | random | Random pick from the filtered pool. **Default pool: all 150** (`--ready` restricts to seeded). Unseeded picks show statement + link (no local tests yet). |
| `walnut daily` | today's problem | Deterministic pick seeded by today's date from **all 150** (stable all day); unseeded shows statement + link. |
| `walnut timer <id> [--minutes M] [--watch]` | interview timer | Arms timer with optional target; `--watch` runs a live rich countdown (red near 0, bell at 0) meant for a second pane. |
| `walnut stats [--topic T]` | dashboard | Overview, by difficulty, by topic (with weak-area highlight), speed sparklines, streak heatmap, **Focus Areas** (see §13). |
| `walnut focus` | drill weakness | Names your weakest pattern (from §13 scoring) and hands you the next problem to practice there. |
| `walnut review` | spaced review | Lists problems due today (interval elapsed) + lapsed ones, sorted by overdue then difficulty. |
| `walnut history [<id>]` | log | Recent solves overall, or full attempt history for one problem. |
| `walnut reset <id> [--hard]` | retry fresh | **Soft (default):** delete `solution.py`, set status back to `unsolved`, clear the active timer — but **keep** `history`, the `review` schedule, and snapshots. **`--hard`:** full wipe — also remove the progress record, review schedule, and `.walnut/snapshots/<slug>/`. |
| `walnut snapshot <id> [name] [--note "…"]` | save a version | Copies your current `solution.py` to `.walnut/snapshots/<slug>/<name-or-timestamp>.py` with an optional note (e.g. "brute-force"). |
| `walnut snapshots <id>` | list versions | Lists saved snapshots for a problem (name, time, note, size). |
| `walnut snapshot diff <id> [a] [b]` | compare | Colored diff between two snapshots, or a snapshot vs. current `solution.py`. |
| `walnut snapshot restore <id> <name>` | roll back | Overwrites `solution.py` with a chosen snapshot (backs up current first). |
| `walnut verify [<id>|--all]` | self-check | Runs each seeded problem's `reference.py` through the runner; asserts all cases pass; validates schema + method signature. Dev/CI + user trust. |
| `walnut config <get|set|list> [key] [value]` | settings | Reads/writes `.walnut/config.json`. |
| `walnut add <slug> [--topic T]` | seed new | Scaffolds a problem dir from `_template/`; opens `problem.json` for authoring. |
| `walnut version` | version | Package + schema versions. |

### Sample outputs

`walnut test 3` (fail then pass):
```
Two Sum · Easy · Arrays & Hashing

  ✓ case 1   nums=[2,7,11,15] target=9
  ✗ case 2   nums=[3,2,4] target=6
      expected  [1, 2]
      got       [0, 1]
  ✓ case 3   nums=[3,3] target=6

  2/3 cases passing  ·  attempt #2
```
```
Two Sum · Easy · Arrays & Hashing

  ✓ case 1   ✓ case 2   ✓ case 3

  ╭────────────────────────────────────────────╮
  │  Solved in 6:20  —  new best! (prev 8:05)   │
  │  first-try: no · streak: 4 days 🔥          │
  ╰────────────────────────────────────────────╯
```

## 13. Progress, Stats & the "What to Improve" Engine

You asked for the signals that best show **what to improve**, so stats are diagnostic first, vanity second. All four core signals are tracked and combined into a per-pattern weakness score.

### 13.1 Metric definitions
- **Solve speed.** `time_sec` = seconds from `active.started_at` (set by `pick`/`open`/`timer`) to the first passing `test`. If no timer was armed, `time_sec = null` and the solve is excluded from speed stats. Reported as best/avg/last, and as a **speed ratio** = `time_sec / target_sec` (targets in §17; >1 = slower than target).
- **First-try success rate.** Fraction of solved problems where `first_try == true` (passed on the first `test` run with `revealed_hints == 0` and `revealed_solution == false`). This measures genuine recall.
- **Attempts to solve.** `attempts` (failed test runs before pass, +1) and calendar days from `first_seen_at` to `solved_at`. High values flag shaky problems.
- **Consistency.** `streak.current`/`longest`, plus active-day set for the heatmap.
- **Efficiency.** Per-problem `slowest_case_sec` vs. budget and stress-case pass rate per pattern — surfaces where your solutions are correct but too slow (a distinct signal from "wrong answer").

### 13.2 Weakness score (per topic)
For each topic (the roadmap's 18 patterns) with ≥1 attempted problem, compute normalized components in `[0,1]` (higher = worse). Scoring is topic-level for M2; finer per-`pattern` ranking is a later enhancement that would require adding `pattern` to `roadmap.json`.

```
fail_component     = 1 - first_try_rate(topic)
attempts_component = clamp((avg_attempts(topic) - 1) / 3, 0, 1)
speed_component    = clamp((avg_speed_ratio(topic) - 1) / 1.5, 0, 1)   # 1.0 → 2.5× target
review_component   = overdue_reviews(topic) / max(1, seen_in_topic)
lapse_component    = clamp(total_lapses(topic) / 3, 0, 1)

weakness = 0.30*fail_component
         + 0.25*attempts_component
         + 0.20*speed_component
         + 0.15*review_component
         + 0.10*lapse_component
```

Weights are defaults in config. Topics are ranked by `weakness` (descending); the top 3 with the single dominant driver (e.g. "slow: avg 2.1× target") appear in the **Focus Areas** panel. `walnut focus` picks the highest-weakness topic and returns its next unsolved (or most-overdue) problem.

### 13.3 `walnut stats` layout (rich)
- **Overview panel:** `solved / 150` big number + overall progress bar; totals by status.
- **By difficulty:** three bars (Easy/Medium/Hard) with solved counts and avg speed ratio.
- **By topic table:** name · `solved/total` bar · first-try% · avg attempts · avg time · a ⚠ marker on weak rows.
- **Speed trend:** per-difficulty sparkline of recent solve times using block glyphs `▁▂▃▄▅▆▇█`.
- **Streak heatmap:** last ~12 weeks as a grid of colored cells (intensity = solves that day).
- **Focus Areas panel:** top weak patterns + the driving reason + a suggested next action.

## 14. Spaced Repetition

An SM-2-lite schedule per solved problem (`review` object). Intervals in days.

**On a successful solve/review (quality `q` derived from speed & first-try, 0–5):**
```
reps += 1
if   reps == 1: interval = 1
elif reps == 2: interval = 3
elif reps == 3: interval = 7
else:           interval = round(prev_interval * ease)
ease = clamp(ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)), 1.3, 3.0)
due  = today + interval days
```
`q` mapping (default): first-try & ≤ target → 5; solved but slow or hinted → 3–4; needed reference → ≤2.

**On a lapse** (fail a due review, or `reset`-then-refail):
```
lapses += 1
reps = 0
interval = 1
ease = max(1.3, ease - 0.20)
due = today + 1 day
```
`walnut review` selects `due <= today`, sorts by most-overdue then hardest.

## 15. Timer / Interview Mode

- Arming: `pick`, `open`, or `timer` set `active = {slug, started_at, target_sec?}`.
- `walnut timer <id> --minutes 30`: sets `target_sec=1800`.
- `--watch`: a blocking `rich.Live` countdown (`mm:ss`), amber < 5:00, red < 1:00, terminal bell (`\a`) at 0, then keeps counting up (overtime) until Ctrl-C. Intended to run in a second pane while you solve.
- On pass, elapsed = `now - started_at`; the success panel reports on-time/over vs target and best-time delta. `active` is cleared.
- Only one `active` attempt at a time; arming a new one warns if another is in progress.

## 16. Terminal Design System (`rich`)

**Palette (semantic styles, defined once in `ui.py`):**

| Token | Style | Used for |
|-------|-------|----------|
| `easy` | green | Easy difficulty |
| `medium` | yellow/gold | Medium difficulty |
| `hard` | red | Hard difficulty |
| `ok` | bold green | pass / solved |
| `bad` | bold red | fail |
| `review` | magenta | due for review |
| `accent` | cyan | headers, ids |
| `muted` | grey42 | secondary text, not-seeded |

**Glyphs:** solved `✓`, attempted `●`, unsolved `○`, no-local-tests `◌`, review-due `↻`, timer `⏱`, streak `🔥` (emoji optional; ASCII fallback).

**Components:**
- Lists → `rich.table.Table(box=box.ROUNDED)`, difficulty column styled per token, header in `accent`.
- Reading → `rich.panel.Panel` with a titled header; examples as an indented sub-block; constraints as a compact list.
- Code → `rich.syntax.Syntax(code, "python", theme="monokai", line_numbers=True)` for `solution`/reference and failing-case context.
- Progress bars → `rich.progress` or a custom unicode bar `█████░░░░░` for compact table cells.
- Sparklines & heatmap → custom helpers using block glyphs and background-colored cells.
- Dashboard → `rich.columns`/`Layout` composing panels.

**Fallbacks:** detect `not sys.stdout.isatty()`, `NO_COLOR`, `TERM=dumb`, or `--plain` → construct `Console(no_color=True)` / plain renderer. If `import rich` fails entirely, a minimal ANSI/plain renderer in `ui.py` provides the same commands without decoration.

## 17. Configuration

`.walnut/config.json` (git-ignored), managed by `walnut config`:

| Key | Default | Meaning |
|-----|---------|---------|
| `editor` | `null` | Command to open files; else `$VISUAL`/`$EDITOR`, else `nano`/`vim`/`notepad` |
| `target_times` | `{"Easy":900,"Medium":1800,"Hard":2700}` | Interview target seconds by difficulty |
| `default_timeouts` | `{"default":10,"stress":20}` | Per-case timeout budgets (seconds) |
| `color` | `"auto"` | `auto`\|`always`\|`never` |
| `daily_pool` | `"all"` | `all` (any of the 150) or `ready` (seeded only) |
| `weakness_weights` | see §13.2 | Tunable scoring weights |
| `language` | `"python"` | Reserved for future multi-language |

## 18. Error Handling & Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (command ok / all tests passed) |
| 1 | Tests failed (`walnut test` with ≥1 failing case) |
| 2 | Usage error / problem not found / not seeded |
| 3 | Environment error (repo not found, `.walnut` unwritable) |

- Import/syntax errors in `solution.py` → treated as a failed run (code 1) with the traceback's final frames shown, never a crash.
- Timeouts → the offending case is marked failed with a "timed out after Ns" note.
- All user-facing errors are single, styled lines (red), no Python traceback unless `--debug`.

## 19. Content Seeding Pipeline

**Source of truth** for a problem is `problem.json` + `starter.py` + `reference.py`. `README.md` is **generated** from `problem.json` (`walnut seed readme <id>` / done at authoring time) so GitHub browsing looks good; the CLI reads `problem.json` directly for statement/hints/cases.

**Authoring a new problem:**
1. `walnut add <slug> --topic <topic-slug>` copies `_template/` into the correct numbered folder and registers it in `roadmap.json`.
2. Fill `problem.json`: original `statement`, `examples`, `constraints`, `hints`, `runner` (entry/method/compare), and `cases` — including `edge` cases and at least one `stress` case (tag each with `kind`).
3. Write `starter.py` (correct `Solution` signature) and `reference.py` (a correct solution).
4. `walnut verify <id>` — must pass (runs `reference.py` against `cases`, checks method name/signature, validates JSON).
5. Set `seeded: true`.

**Method-name authority:** the `Solution` method (or class for design problems) is fixed in `roadmap.json.method` and `problem.json.runner`. Even **non-seeded** problems ship a `starter.py` with the correct method name so you can start coding any of the 150 immediately (you just won't have local tests until it's seeded).

**Seed order:** M1 seeds **Arrays & Hashing (9)** + **Two Pointers (5)**. Then, in roadmap order: Sliding Window → Stack → Binary Search → Linked List → Trees → Tries → Heap → Backtracking → Graphs → Advanced Graphs → 1-D DP → 2-D DP → Greedy → Intervals → Math & Geometry → Bit Manipulation.

**Restatement rule (legal):** never paste LeetCode/NeetCode text. Write the problem in your own words, generate your own cases, and link to the official problem. See §E.

## 20. Build Milestones

| Milestone | Deliverable | Definition of done |
|-----------|-------------|--------------------|
| **M0 Scaffold** | Repo, `pyproject.toml`, `.gitignore`, package skeleton, `roadmap.json` + a minimal `problem.json` for all 150 (metadata, links, placeholder statement for unseeded), generated `starter.py` for all 150, `walnut topics/list/show/doctor` | `pip install -e .` works; `walnut topics` lists 18 topics/150; `walnut show <id>` works for any problem (statement or link) |
| **M1 Runner + first topics** | `runner.py`, `progress.py`; `pick/open/test/run/reset`; thread-based timeouts; seed Arrays & Hashing + Two Pointers (14 problems: statements, hints, cases tagged example/edge/stress, references); `walnut verify` | `walnut verify --all` green (14/14); solving Two Sum end-to-end works and records time; a too-slow solution trips a stress-case timeout |
| **M2 Stats** | `stats.py` + weakness engine; `stats/focus/history`; streaks | `walnut stats` shows dashboard; `walnut focus` returns a sensible next problem |
| **M3 Review + Timer** | `review.py`, `timer.py`; `review`, `timer --watch` | Scheduling matches §14; countdown works in a second pane |
| **M4 Polish** | Full `rich` UI (panels, syntax, sparklines, heatmap), `config`, `--plain`, plain fallback; `walnut snapshot`/`snapshots`/`diff`/`restore`, `test --perf` timing | Looks good in a real terminal; degrades cleanly when piped; snapshots + diffs work |
| **M5 Seed all** | Seed remaining 16 topics; add `design`/`roundtrip`/`checker` entries as needed | `walnut verify --all` green for all seeded; ≥1 solid case set per problem |

Each milestone is independently useful; M0–M1 already give a working offline trainer.

## 21. Testing & Verification

- **Unit tests** (`tests/`, pytest): comparison modes (`exact/sorted/groups/approx/bool`), deep-copy isolation, timeout behavior, roundtrip entry, progress transitions (attempt→solve, first_try logic, streak math), review scheduling formulas, weakness scoring.
- **`walnut verify --all`**: every seeded `reference.py` must pass its own `cases` through the exact runner used by `walnut test` (the runner is called with `module_filename="reference.py"` so verify and test share identical execution/compare logic). Doubles as user trust ("the answers really pass").
- **Schema validation**: `problem.json` required fields, `cases[].args` keys match the method's parameter names (introspect via `inspect.signature`).
- **Optional CI**: GitHub Action runs pytest + `walnut verify --all` on push.
- **Smoke script**: `walnut topics`, `walnut list arrays-and-hashing`, `walnut show 3`, `walnut daily`, `walnut next` produce non-empty, non-erroring output.

## 22. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Copyright of problem statements | Original restatements only; link out; legal note in README |
| Premium problems (271, 286, 261, 323, 269, 252, 253) | Restated by us; tests run offline regardless; note that the LeetCode link may hit a paywall |
| Infinite loops / hangs in user code | Per-case timeout (SIGALRM on Unix; thread-future on Windows) |
| Solutions that mutate inputs | Deep-copy args per case |
| Multiple valid answers | `sorted`/`groups` compare modes, or a `checker.py` (`entry:"checker"`) |
| Non-determinism (daily/random) | Seed RNG with the date / explicit seed |
| `rich` unavailable offline | Built-in plain-text fallback renderer (vendoring explicitly out of scope — see §8) |
| Windows timeouts can't hard-kill a thread | Accepted trade-off of the chosen thread-based approach; report timeout + move on. Subprocess isolation is the documented upgrade path if bulletproof cross-OS kill is ever needed |
| Big inputs / recursion depth (Trees, DP) | Keep shipped cases reasonable; note `sys.setrecursionlimit` where relevant |

## 23. Resolved Decisions (previously open)

All prior open questions are now settled — nothing blocks implementation.

| # | Question | Decision | Impact |
|---|----------|----------|--------|
| 1 | Timeout strategy | **Thread-based best-effort** — SIGALRM hard-stop on mac/Linux, thread-future on Windows; generous per-case budgets | §11 step 5, §11a |
| 2 | Vendor `rich`? | **No** — rely on `pip` at install; built-in plain-text fallback if absent | §8 |
| 3 | Solution snapshots | **Yes** — versioned snapshots under `.walnut/snapshots/<slug>/` via `walnut snapshot`/`snapshots`/`diff`/`restore` | §7, §10.3, §12 |
| 4 | Progress portability | **Local only** — no export; a fresh clone starts at zero | §2, §10.3 |
| 5 | Daily/random pool | **All 150** — unseeded picks show statement + link | §12, §17 |
| 6 | Multi-language | **Reserve schema, build Python-only** (see §23a) | §10.1, §17, §23a |

### 23a. Multi-language readiness (reserved, not built)
The schema leaves room so a later version can add languages without a redesign — none of this is built in v1:
- `roadmap.json.language` and `config.language` select the active language.
- Per-problem files become language-suffixed: `solution.py` / `solution.js` / `solution.java`, with matching `starter.<ext>` / `reference.<ext>`; `.gitignore` ignores `**/solution.*`.
- `runner` gains a `lang_entry` map (per-language method/compile/run command); v1 implements only the Python path.

## 24. Review Resolutions

Answers to the implementation review. These are **binding**; where a section was corrected, it's noted.

### Blocking
1. **Seed content authorship.** M1 authors original statements, hints, references, and cases for the 14 seeded problems (Arrays & Hashing + Two Pointers). Only Two Sum is fully worked in Appendix B as the template to follow; the other 13 are authored to the same shape, and every `reference.py` must pass `walnut verify`.
2. **Generated stress cases.** A case may declare a generator instead of inline `args`: `{ "kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 10 }`. The generator lives in an optional, tracked `fixtures.py` in the problem dir exposing `make_case(seed) -> {"args": {...}, "expected": ...}`. Absent `gen`, inline `args`/`expected` are used. (Schema row added to §10.2.)
3. **verify vs. solution.py.** `runner.run()` takes `module_filename` (default `"solution.py"`; `verify` passes `"reference.py"`). See §11 step 1 and §21.
4. **Windows timeout.** Report the case as timed out and continue; a non-returning worker thread may linger until process exit — no hard-kill guarantee on Windows (accepted; §11 step 5, §22). Subprocess isolation is the documented upgrade path.
5. **Timer conflict.** Arming a timer while a *different* `active` slug is in progress → abort with a message unless `--force` (which discards the old timer). Re-arming the same slug just continues it.
6. **`test` progress transitions.** Every `walnut test` increments `test_runs`. While `status != solved`, each failing run increments an internal `failed_before_solve`. On the first all-pass: `attempts = failed_before_solve + 1`, `status = solved`, `solved_at = now`, `first_try = (failed_before_solve == 0 and revealed_hints == 0 and revealed_solution == false)`, and `history` is appended. Passes *after* solve append `history` and may update `best_time_sec`/review, but never change `attempts` or `first_try`.
7. **`run` is inert.** `walnut run` never mutates progress — not `test_runs`, `attempts`, or `first_try`. Pure dry-run.
8. **Spaced-rep quality `q`.** Exactly: `q=5` first-try AND within target time; `q=4` first-try but over target (no hints/reference); `q=3` solved with ≤1 hint OR after exactly one failed run; `q=2` solved with ≥2 hints or ≥2 failed runs; `q=1` reference revealed before solving, or a lapse (failed a due review). (Refines §14. This separates an earlier conflation of "first-try slow" with "failed tests" into `q=4` vs `q=3/2`.)
9. **Streak timezone.** Keyed by the **local calendar date at the moment of the passing `test`**. Multiple solves same day → `current` unchanged. Solve on the day after `last_solved_date` → `current += 1`. Gap > 1 day → `current = 1`. A timer started before midnight but passed after counts on the pass date. `longest = max(longest, current)`.
10. **Unseeded commands.** `test`, `run`, `hint`, `solution`, `verify` on an unseeded problem → exit 2 with "not seeded yet — see the LeetCode link". `show` works (metadata + placeholder statement + link). `pick`/`open` work (starter has the correct signature) but warn that there are no local tests yet.
11. **Editor launch.** Resolve editor = `config.editor` → `$VISUAL` → `$EDITOR` → first available of `nano`/`vim`/`notepad`. Parse with `shlex.split`. Launch **blocking** (wait for close). Non-zero exit → print a warning but don't fail the command; nothing resolves → print the file path instead.
12. **Signature validation.** `method`/`roundtrip`: every `cases[].args` key must be a parameter of the target method; params with defaults may be omitted, unexpected keys error, `*args`/positional-only skip the check with a warning. `design`: validate `ops`/`args`/`expected` equal length. `checker`: require only `args`. (Refines §21.)

### Non-blocking
1. **`--json`.** Supported on `list`, `stats`, `history`, `topics`, `doctor` (schema mirrors the underlying dict, documented in `--help`); other commands ignore it.
2. **`<topic>` resolution.** Accepts topic id (1–18), slug, exact name, or unambiguous slug/name prefix.
3. **Ambiguous slug prefix.** Error and list the candidate matches.
4. **Traceback frames.** Show the last 3 frames + the exception message; full traceback with `--debug`.
5. **Import-time hangs.** The import step is inside the timeout (module load counts against the first case's budget).
6. **`approx`.** Scalars and (possibly nested) numeric lists via element-wise tolerance; non-numeric falls back to `exact`.
7. **`sorted`/`groups` on unsortable types.** Catch `TypeError` and fail that case with an "uncomparable output" message instead of crashing.
8. **`history[].result`.** One of `pass` | `fail` | `error` | `timeout`.
9. **Missing speed data.** If a topic has no timed solves, `speed_component` is dropped and the remaining weights are renormalized (not treated as 0).
10. **`reset --hard` + snapshots.** `--hard` deletes snapshots; soft `reset` keeps them (§12).

### Accepted assumptions & contradiction fixes
The proposed assumptions are accepted as above (with the `q`-mapping tightened per Blocking 8). All 10 contradictions found in review are corrected inline: default-pool wording (Appendix E), M0 minimal `problem.json` (§20), `cases[].kind` optional-default-`example` (§10.2, Appendix B), runner `module_filename` (§11/§21), Windows-timeout wording (§11/§22), `reset`/`--hard` split (§12), topic-level weakness (§13.2), vendoring removed (§22), checker case shape (§11), and design `ops/args/expected` arrays (§11).

---

# Part III — Appendices

## Appendix A — Full NeetCode 150

Global id · Title · LeetCode # · Difficulty · Primary `Solution` method (`*` = design/class-based). **Bold** = seeded in M1.

### 1. Arrays & Hashing (9)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| **1** | **Contains Duplicate** | 217 | Easy | `hasDuplicate` |
| **2** | **Valid Anagram** | 242 | Easy | `isAnagram` |
| **3** | **Two Sum** | 1 | Easy | `twoSum` |
| **4** | **Group Anagrams** | 49 | Medium | `groupAnagrams` |
| **5** | **Top K Frequent Elements** | 347 | Medium | `topKFrequent` |
| **6** | **Encode and Decode Strings** | 271 | Medium | `encode`/`decode`* |
| **7** | **Product of Array Except Self** | 238 | Medium | `productExceptSelf` |
| **8** | **Valid Sudoku** | 36 | Medium | `isValidSudoku` |
| **9** | **Longest Consecutive Sequence** | 128 | Medium | `longestConsecutive` |

### 2. Two Pointers (5)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| **10** | **Valid Palindrome** | 125 | Easy | `isPalindrome` |
| **11** | **Two Sum II** | 167 | Medium | `twoSum` |
| **12** | **3Sum** | 15 | Medium | `threeSum` |
| **13** | **Container With Most Water** | 11 | Medium | `maxArea` |
| **14** | **Trapping Rain Water** | 42 | Hard | `trap` |

### 3. Sliding Window (6)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 15 | Best Time to Buy and Sell Stock | 121 | Easy | `maxProfit` |
| 16 | Longest Substring Without Repeating Characters | 3 | Medium | `lengthOfLongestSubstring` |
| 17 | Longest Repeating Character Replacement | 424 | Medium | `characterReplacement` |
| 18 | Permutation in String | 567 | Medium | `checkInclusion` |
| 19 | Minimum Window Substring | 76 | Hard | `minWindow` |
| 20 | Sliding Window Maximum | 239 | Hard | `maxSlidingWindow` |

### 4. Stack (7)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 21 | Valid Parentheses | 20 | Easy | `isValid` |
| 22 | Min Stack | 155 | Medium | `MinStack`* |
| 23 | Evaluate Reverse Polish Notation | 150 | Medium | `evalRPN` |
| 24 | Generate Parentheses | 22 | Medium | `generateParenthesis` |
| 25 | Daily Temperatures | 739 | Medium | `dailyTemperatures` |
| 26 | Car Fleet | 853 | Medium | `carFleet` |
| 27 | Largest Rectangle in Histogram | 84 | Hard | `largestRectangleArea` |

### 5. Binary Search (7)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 28 | Binary Search | 704 | Easy | `search` |
| 29 | Search a 2D Matrix | 74 | Medium | `searchMatrix` |
| 30 | Koko Eating Bananas | 875 | Medium | `minEatingSpeed` |
| 31 | Find Minimum in Rotated Sorted Array | 153 | Medium | `findMin` |
| 32 | Search in Rotated Sorted Array | 33 | Medium | `search` |
| 33 | Time Based Key-Value Store | 981 | Medium | `TimeMap`* |
| 34 | Median of Two Sorted Arrays | 4 | Hard | `findMedianSortedArrays` |

### 6. Linked List (11)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 35 | Reverse Linked List | 206 | Easy | `reverseList` |
| 36 | Merge Two Sorted Lists | 21 | Easy | `mergeTwoLists` |
| 37 | Reorder List | 143 | Medium | `reorderList` |
| 38 | Remove Nth Node From End of List | 19 | Medium | `removeNthFromEnd` |
| 39 | Copy List With Random Pointer | 138 | Medium | `copyRandomList` |
| 40 | Add Two Numbers | 2 | Medium | `addTwoNumbers` |
| 41 | Linked List Cycle | 141 | Easy | `hasCycle` |
| 42 | Find the Duplicate Number | 287 | Medium | `findDuplicate` |
| 43 | LRU Cache | 146 | Medium | `LRUCache`* |
| 44 | Merge K Sorted Lists | 23 | Hard | `mergeKLists` |
| 45 | Reverse Nodes in K-Group | 25 | Hard | `reverseKGroup` |

### 7. Trees (15)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 46 | Invert Binary Tree | 226 | Easy | `invertTree` |
| 47 | Maximum Depth of Binary Tree | 104 | Easy | `maxDepth` |
| 48 | Diameter of Binary Tree | 543 | Easy | `diameterOfBinaryTree` |
| 49 | Balanced Binary Tree | 110 | Easy | `isBalanced` |
| 50 | Same Tree | 100 | Easy | `isSameTree` |
| 51 | Subtree of Another Tree | 572 | Easy | `isSubtree` |
| 52 | Lowest Common Ancestor of a BST | 235 | Medium | `lowestCommonAncestor` |
| 53 | Binary Tree Level Order Traversal | 102 | Medium | `levelOrder` |
| 54 | Binary Tree Right Side View | 199 | Medium | `rightSideView` |
| 55 | Count Good Nodes in Binary Tree | 1448 | Medium | `goodNodes` |
| 56 | Validate Binary Search Tree | 98 | Medium | `isValidBST` |
| 57 | Kth Smallest Element in a BST | 230 | Medium | `kthSmallest` |
| 58 | Construct Binary Tree from Preorder and Inorder | 105 | Medium | `buildTree` |
| 59 | Binary Tree Maximum Path Sum | 124 | Hard | `maxPathSum` |
| 60 | Serialize and Deserialize Binary Tree | 297 | Hard | `Codec`* |

### 8. Tries (3)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 61 | Implement Trie (Prefix Tree) | 208 | Medium | `Trie`* |
| 62 | Design Add and Search Words Data Structure | 211 | Medium | `WordDictionary`* |
| 63 | Word Search II | 212 | Hard | `findWords` |

### 9. Heap / Priority Queue (7)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 64 | Kth Largest Element in a Stream | 703 | Easy | `KthLargest`* |
| 65 | Last Stone Weight | 1046 | Easy | `lastStoneWeight` |
| 66 | K Closest Points to Origin | 973 | Medium | `kClosest` |
| 67 | Kth Largest Element in an Array | 215 | Medium | `findKthLargest` |
| 68 | Task Scheduler | 621 | Medium | `leastInterval` |
| 69 | Design Twitter | 355 | Medium | `Twitter`* |
| 70 | Find Median From Data Stream | 295 | Hard | `MedianFinder`* |

### 10. Backtracking (9)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 71 | Subsets | 78 | Medium | `subsets` |
| 72 | Combination Sum | 39 | Medium | `combinationSum` |
| 73 | Permutations | 46 | Medium | `permute` |
| 74 | Subsets II | 90 | Medium | `subsetsWithDup` |
| 75 | Combination Sum II | 40 | Medium | `combinationSum2` |
| 76 | Word Search | 79 | Medium | `exist` |
| 77 | Palindrome Partitioning | 131 | Medium | `partition` |
| 78 | Letter Combinations of a Phone Number | 17 | Medium | `letterCombinations` |
| 79 | N-Queens | 51 | Hard | `solveNQueens` |

### 11. Graphs (13)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 80 | Number of Islands | 200 | Medium | `numIslands` |
| 81 | Max Area of Island | 695 | Medium | `maxAreaOfIsland` |
| 82 | Clone Graph | 133 | Medium | `cloneGraph` |
| 83 | Walls and Gates | 286 | Medium | `wallsAndGates` |
| 84 | Rotting Oranges | 994 | Medium | `orangesRotting` |
| 85 | Pacific Atlantic Water Flow | 417 | Medium | `pacificAtlantic` |
| 86 | Surrounded Regions | 130 | Medium | `solve` |
| 87 | Course Schedule | 207 | Medium | `canFinish` |
| 88 | Course Schedule II | 210 | Medium | `findOrder` |
| 89 | Graph Valid Tree | 261 | Medium | `validTree` |
| 90 | Number of Connected Components in an Undirected Graph | 323 | Medium | `countComponents` |
| 91 | Redundant Connection | 684 | Medium | `findRedundantConnection` |
| 92 | Word Ladder | 127 | Hard | `ladderLength` |

### 12. Advanced Graphs (6)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 93 | Reconstruct Itinerary | 332 | Hard | `findItinerary` |
| 94 | Min Cost to Connect All Points | 1584 | Medium | `minCostConnectPoints` |
| 95 | Network Delay Time | 743 | Medium | `networkDelayTime` |
| 96 | Swim in Rising Water | 778 | Hard | `swimInWater` |
| 97 | Alien Dictionary | 269 | Hard | `foreignDictionary` |
| 98 | Cheapest Flights Within K Stops | 787 | Medium | `findCheapestPrice` |

### 13. 1-D Dynamic Programming (12)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 99 | Climbing Stairs | 70 | Easy | `climbStairs` |
| 100 | Min Cost Climbing Stairs | 746 | Easy | `minCostClimbingStairs` |
| 101 | House Robber | 198 | Medium | `rob` |
| 102 | House Robber II | 213 | Medium | `rob` |
| 103 | Longest Palindromic Substring | 5 | Medium | `longestPalindrome` |
| 104 | Palindromic Substrings | 647 | Medium | `countSubstrings` |
| 105 | Decode Ways | 91 | Medium | `numDecodings` |
| 106 | Coin Change | 322 | Medium | `coinChange` |
| 107 | Maximum Product Subarray | 152 | Medium | `maxProduct` |
| 108 | Word Break | 139 | Medium | `wordBreak` |
| 109 | Longest Increasing Subsequence | 300 | Medium | `lengthOfLIS` |
| 110 | Partition Equal Subset Sum | 416 | Medium | `canPartition` |

### 14. 2-D Dynamic Programming (11)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 111 | Unique Paths | 62 | Medium | `uniquePaths` |
| 112 | Longest Common Subsequence | 1143 | Medium | `longestCommonSubsequence` |
| 113 | Best Time to Buy and Sell Stock With Cooldown | 309 | Medium | `maxProfit` |
| 114 | Coin Change II | 518 | Medium | `change` |
| 115 | Target Sum | 494 | Medium | `findTargetSumWays` |
| 116 | Interleaving String | 97 | Medium | `isInterleave` |
| 117 | Longest Increasing Path in a Matrix | 329 | Hard | `longestIncreasingPath` |
| 118 | Distinct Subsequences | 115 | Hard | `numDistinct` |
| 119 | Edit Distance | 72 | Medium | `minDistance` |
| 120 | Burst Balloons | 312 | Hard | `maxCoins` |
| 121 | Regular Expression Matching | 10 | Hard | `isMatch` |

### 15. Greedy (8)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 122 | Maximum Subarray | 53 | Medium | `maxSubArray` |
| 123 | Jump Game | 55 | Medium | `canJump` |
| 124 | Jump Game II | 45 | Medium | `jump` |
| 125 | Gas Station | 134 | Medium | `canCompleteCircuit` |
| 126 | Hand of Straights | 846 | Medium | `isNStraightHand` |
| 127 | Merge Triplets to Form Target Triplet | 1899 | Medium | `mergeTriplets` |
| 128 | Partition Labels | 763 | Medium | `partitionLabels` |
| 129 | Valid Parenthesis String | 678 | Medium | `checkValidString` |

### 16. Intervals (6)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 130 | Insert Interval | 57 | Medium | `insert` |
| 131 | Merge Intervals | 56 | Medium | `merge` |
| 132 | Non-Overlapping Intervals | 435 | Medium | `eraseOverlapIntervals` |
| 133 | Meeting Rooms | 252 | Easy | `canAttendMeetings` |
| 134 | Meeting Rooms II | 253 | Medium | `minMeetingRooms` |
| 135 | Minimum Interval to Include Each Query | 1851 | Hard | `minInterval` |

### 17. Math & Geometry (8)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 136 | Rotate Image | 48 | Medium | `rotate` |
| 137 | Spiral Matrix | 54 | Medium | `spiralOrder` |
| 138 | Set Matrix Zeroes | 73 | Medium | `setZeroes` |
| 139 | Happy Number | 202 | Easy | `isHappy` |
| 140 | Plus One | 66 | Easy | `plusOne` |
| 141 | Pow(x, n) | 50 | Medium | `myPow` |
| 142 | Multiply Strings | 43 | Medium | `multiply` |
| 143 | Detect Squares | 2013 | Medium | `DetectSquares`* |

### 18. Bit Manipulation (7)
| # | Title | LC | Diff | Method |
|--|-------|----|------|--------|
| 144 | Single Number | 136 | Easy | `singleNumber` |
| 145 | Number of 1 Bits | 191 | Easy | `hammingWeight` |
| 146 | Counting Bits | 338 | Easy | `countBits` |
| 147 | Reverse Bits | 190 | Easy | `reverseBits` |
| 148 | Missing Number | 268 | Easy | `missingNumber` |
| 149 | Sum of Two Integers | 371 | Medium | `getSum` |
| 150 | Reverse Integer | 7 | Medium | `reverse` |

**Totals:** 9+5+6+7+7+11+15+3+7+9+13+6+12+11+8+6+8+7 = **150**. Difficulty mix ≈ 34 Easy / 94 Medium / 22 Hard.

## Appendix B — Example `problem.json` (Two Sum, fully specified)

```json
{
  "id": 3,
  "slug": "two-sum",
  "title": "Two Sum",
  "difficulty": "Easy",
  "topic": "Arrays & Hashing",
  "topic_slug": "arrays-and-hashing",
  "leetcode": 1,
  "leetcode_url": "https://leetcode.com/problems/two-sum/",
  "neetcode_url": null,
  "pattern": "Hash map complement lookup",
  "seeded": true,
  "runner": { "entry": "method", "method": "twoSum", "compare": "sorted", "timeout_sec": 5 },
  "statement": "Given an array of integers `nums` and an integer `target`, return the indices of the two numbers that add up to `target`. Assume exactly one valid pair exists, and you may not reuse the same element.",
  "examples": [
    { "input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "nums[0] + nums[1] = 2 + 7 = 9." },
    { "input": "nums = [3,2,4], target = 6", "output": "[1,2]", "explanation": "nums[1] + nums[2] = 2 + 4 = 6." }
  ],
  "constraints": [
    "2 <= nums.length <= 10^4",
    "-10^9 <= nums[i] <= 10^9",
    "Exactly one valid answer exists."
  ],
  "hints": [
    "Brute force checks every pair in O(n^2). Can you trade space for time?",
    "As you scan, keep a hash map of value -> index you've already seen.",
    "For the current number x, look up target - x BEFORE inserting x, so you never reuse an index."
  ],
  "cases": [
    { "kind": "example", "args": { "nums": [2,7,11,15], "target": 9 }, "expected": [0,1] },
    { "kind": "example", "args": { "nums": [3,2,4], "target": 6 }, "expected": [1,2] },
    { "kind": "edge", "note": "duplicate values", "args": { "nums": [3,3], "target": 6 }, "expected": [0,1] },
    { "kind": "edge", "note": "negatives sum to zero", "args": { "nums": [-3,4,3,90], "target": 0 }, "expected": [0,2] },
    { "kind": "stress", "note": "n=100000 (generated); a naive O(n^2) times out", "timeout_sec": 10, "args": { "nums": "[generated 0..99999]", "target": 199997 }, "expected": [99998, 99999] }
  ]
}
```

Corresponding `starter.py`:
```python
from __future__ import annotations


class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        # Your code here
        pass
```

Corresponding `reference.py`:
```python
class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, n in enumerate(nums):
            if target - n in seen:
                return [seen[target - n], i]
            seen[n] = i
        return []
```

**On stress cases:** large `stress` inputs are typically **generated** (in a small helper or inside `reference.py`) rather than inlined as literals — the fields that matter in `problem.json` are `kind`, `note`, `timeout_sec`, and the expected result. A correct O(n) Two Sum clears the 10s budget instantly; an O(n²) scan of 100k elements won't, which is the bottleneck signal.

**Roundtrip example** (Encode and Decode Strings): `runner = {"entry":"roundtrip","encode":"encode","decode":"decode","compare":"exact"}`, and each case is `{"kind":"example","args": {"strs": ["neet","co#de",""]}, "expected": ["neet","co#de",""]}` (expected equals the input list; the runner checks `decode(encode(strs)) == strs`).

## Appendix C — Packaging & ignore files

`pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "walnut"
version = "0.1.0"
description = "Offline NeetCode-150 practice CLI"
requires-python = ">=3.9"
dependencies = ["rich>=13"]

[project.scripts]
walnut = "walnut.cli:main"

[tool.setuptools]
packages = ["walnut"]
```

`.gitignore`:
```gitignore
# your attempts + local progress — never committed
**/solution.py
.walnut/

# python noise
__pycache__/
*.pyc
.venv/
*.egg-info/
build/
dist/

# os noise
.DS_Store
```

**Starter/reference conventions:**
- `starter.py` uses `from __future__ import annotations` so modern type hints (`list[int]`) are safe on 3.9; body is `# Your code here` + `pass`.
- Non-seeded starters still carry the correct method name; design problems get a `class Solution:`/named-class stub with a "see LeetCode for the interface" comment.
- `reference.py` is a clean, idiomatic solution (no annotations required); it must pass `walnut verify`.

## Appendix D — Command cheat sheet

```
walnut                      dashboard (daily, streak, reviews due, next)
walnut doctor               verify environment / show repo path
walnut topics               progress across the 18 patterns
walnut list [topic]         browse problems (filters: --difficulty --status --ready --due)
walnut show <id>            read a problem
walnut pick <id> [--open]   start solving (creates solution.py, starts timer)
walnut open <id>            open your solution in $EDITOR
walnut test <id>            run local tests (records time + progress on pass)
walnut run <id>             run tests without touching progress
walnut hint <id> [n]        reveal the next hint
walnut solution <id>        show the reference solution
walnut timer <id> --minutes 30 --watch   live interview countdown
walnut next | random | daily              get a problem to work on
walnut stats | focus        diagnostics: what to improve, and drill it
walnut review               problems due for spaced review
walnut history [<id>]       your solve log
walnut reset <id>           wipe your solution + progress for a retry
walnut verify --all         prove every seeded reference passes its cases
walnut add <slug> --topic … seed a new problem
```

## Appendix E — Glossary, credits & legal

- **Seeded:** a problem that ships with local test cases + a reference solution (so `walnut test`/`walnut solution` work offline).
- **Ready pool:** the set of seeded problems. `daily`/`random` default to **all 150**; use `--ready` (or set `daily_pool` in config) to restrict to this pool.
- **First-try:** solved on the first `test` run with no hints and no reference revealed.
- **Speed ratio:** `time_sec / target_sec` for the difficulty (>1 = slower than target).

**Credits:** Problem selection and topic ordering follow the **NeetCode roadmap** (neetcode.io). Problems originate from **LeetCode**.

**Legal note:** This repo contains **no** copyrighted problem text from LeetCode or NeetCode. Every statement is an original restatement written for this project, and each problem links to its official LeetCode page. Reference solutions and test cases are original. This project is unaffiliated with and unendorsed by LeetCode or NeetCode. Keep your git repo private if you prefer; do not commit copyrighted statements if you edit the restatements.
```

---

*End of document. Suggested next step: implement M0 + M1 (a working offline trainer with Arrays & Hashing + Two Pointers), then iterate through M2–M5.*
