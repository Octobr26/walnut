# Walnut Repo Guide

This repo is split into three things:

- The CLI application in `walnut/`.
- The problem catalog in `roadmap.json` and `problems/`.
- Your local-only work in ignored files like `solution.py`, `notes.md`, and `.walnut/`.

## Command Shortcut

Fastest setup from the repo root:

```bash
./setup
```

After install, the short command should be:

```bash
walnut
walnut doctor
walnut topics
walnut show 3
```

You can run `walnut` from any directory after setup.
The wrapper points back to this clone, and this repo remains the source of truth for roadmap content, local progress, attempts, and notes.

In an interactive terminal, plain `walnut` opens the TUI.
Use `walnut home` for the static dashboard.

If your shell says `walnut: command not found`, use the PATH fix in [Quickstart](QUICKSTART.md#if-walnut-is-not-found).

There is also a `Makefile` for common repo tasks:

```bash
make setup
make install
make doctor
make topics
make list TOPIC=two-pointers
make show ID=3
make pick ID=3
make test ID=3
make run ID=3
make verify
make unit
make smoke
make sync
make links ID=3
make notes ID=3
make tui
```

## Top-Level Map

```text
README.md                         quickstart
walnut-plan-and-technical-design.md
pyproject.toml                    package metadata and console entry point
setup                             local venv installer and command wrapper writer
roadmap.json                      master index of all 150 problems
Makefile                          short local commands

walnut/                           CLI source code
docs/                             quickstart, repo guide, and cheat sheets
problems/                         problem catalog and seeded content
tests/                            unit and smoke tests
tools/seed_content.py             regenerates the roadmap/problem skeleton
_template/                        starter files for future seeded problems
.walnut/                          local progress and timers, ignored
```

## CLI Source

```text
walnut/cli.py        argparse commands and command output
walnut/repo.py       repo discovery, roadmap loading, id/slug/topic resolution
walnut/files.py      local solution and notes file creation
walnut/runner.py     imports solution/reference modules, runs cases, compares output
walnut/progress.py   reads/writes .walnut/progress.json and solve history
walnut/tui.py        Textual terminal interface
walnut/neetcode.py   safe NeetCode roadmap metadata sync
```

Most command behavior starts in `walnut/cli.py`. If a command needs a problem, it resolves
through `walnut/repo.py`. If it runs code, it goes through `walnut/runner.py`. If it mutates
local progress, it goes through `walnut/progress.py`.

## Problem Folders

Each problem lives under its topic:

```text
problems/01-arrays-and-hashing/03-two-sum/
  problem.json      machine-readable statement, runner config, hints, cases
  README.md         generated human-readable problem page
  starter.py        copied to solution.py by walnut pick
  reference.py      reference solution for seeded problems
  fixtures.py       optional generated stress-case data
  solution.py       your local attempt, ignored
  notes.md          your local notes, ignored
```

Only the first 14 problems are fully seeded right now:

- Arrays & Hashing
- Two Pointers

The other problems have metadata, links, placeholder statements, and starters.

## Daily Workflow

Browse:

```bash
walnut
walnut topics
walnut list arrays-and-hashing
walnut show 3
```

Solve:

```bash
walnut pick 3
# edit problems/01-arrays-and-hashing/03-two-sum/solution.py
walnut test 3 --perf
```

Use the default output for the Rich terminal view. Add `--plain` when you need
stable text for scripts, logs, or copying into another tool.

Use official links without copying protected content:

```bash
walnut open-official 3 --site leetcode --print
walnut open-official 3 --site neetcode --print
```

Keep private notes:

```bash
walnut notes 3
```

## Testing

Run the Python tests:

```bash
.venv/bin/python -m unittest discover -s tests
```

Verify all seeded reference solutions against local cases:

```bash
walnut verify --all --plain
```

Run both plus a couple of smoke checks:

```bash
make smoke
```

## Roadmap Sync

`walnut sync-roadmap` fetches public NeetCode roadmap metadata only:

- problem titles
- topic labels
- difficulty
- LeetCode IDs and URLs
- NeetCode problem URLs

It intentionally does not copy LeetCode/NeetCode statements, explanations, videos, or solution text.

Check drift:

```bash
walnut sync-roadmap --plain
```

Apply safe metadata fields:

```bash
walnut sync-roadmap --apply --plain
```

Topic moves are currently report-only because moving folders safely needs a separate migration.

## Local State

These are intentionally ignored:

```text
**/solution.py
**/notes.md
.walnut/
```

That means your attempts, notes, timers, and progress stay local and do not pollute
the repo.
