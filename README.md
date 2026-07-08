# walnut

`walnut` is an offline, terminal-first NeetCode 150 practice CLI. It ships local
problem metadata, starters, reference solutions for seeded problems, a Python
runner, and local-only progress tracking under `.walnut/`.

Fast setup:

```bash
./setup
```

Then:

```bash
walnut
walnut topics
walnut show 3
walnut pick 3
walnut test 3 --perf
```

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for the lowest-friction usage path.
See [docs/REPO_GUIDE.md](docs/REPO_GUIDE.md) for a map of the repo and everyday commands.

```bash
./setup
walnut
walnut doctor
walnut topics
walnut show 3
walnut pick 3
walnut test 3
walnut sync-roadmap
walnut open-official 3 --print
walnut notes 3
walnut cheat 3
```

`walnut tui` opens a browse-and-preview interface: left pane tabs for topics
(enter to drill in, esc to back out) and the flat problem list, right pane shows
the highlighted problem, bottom bar tracks the active problem, timer, and last
test result.
Running plain `walnut` opens that interface in an interactive terminal; use
`walnut home` for the static dashboard.
Keys: `j/k` move, `[`/`]` switch tabs, `enter` open topic, `s` start,
`r` reset, `n` notes, `c` cheat sheet, `/` filter, `q` quit. Run tests from a second terminal with `walnut test <id>`;
the TUI picks up results within a second.

Per-topic cheat sheets live in `docs/cheatsheets/` (18 topics plus `python-stdlib`
and `complexity`). `walnut cheat` shows the sheet for the active problem's topic;
`walnut cheat <topic|problem id|python|complexity>` targets one directly, and
`walnut cheat --list` shows all sheets.

If `walnut` is not found after installing, add the local command directory to
your `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

You can also use the included `Makefile`:

```bash
make setup
make doctor
make topics
make show ID=3
make test ID=3
make verify
```

Use the default output for the nicer Rich terminal view. Add `--plain` when you
want script-friendly text.

Personal solution files live beside each problem as `solution.py` and are ignored
by git. Personal notes can live beside each problem as `notes.md` and are ignored
by git too. Progress and timers live in `.walnut/` and are ignored too.

`walnut sync-roadmap` refreshes public NeetCode roadmap metadata only: titles,
topic labels, difficulty, LeetCode IDs, and links. It intentionally does not
copy LeetCode/NeetCode statements, explanations, or solution text.

This project links to LeetCode and follows the NeetCode 150 ordering, but all
included statements, test cases, and reference solutions are original.
