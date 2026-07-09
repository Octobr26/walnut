<h1 align="center">🌰 walnut</h1>

<p align="center">
  <strong>Offline LeetCode CLI for terminal-native practice.</strong>
</p>

<p align="center">
  <img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="Rich and Textual" src="https://img.shields.io/badge/TUI-Rich%20%2B%20Textual-111827?style=flat-square">
  <img alt="Offline LeetCode CLI" src="https://img.shields.io/badge/use-offline%20LeetCode%20CLI-16A34A?style=flat-square">
  <img alt="NeetCode 150" src="https://img.shields.io/badge/roadmap-NeetCode%20150-F97316?style=flat-square">
  <img alt="Local only" src="https://img.shields.io/badge/data-local--only-7C3AED?style=flat-square">
</p>

Offline LeetCode CLI I built because nothing kills practice momentum like spotty Wi-Fi on a flight or terrible hotel internet.

Local problems, test runner, starter templates, reference solutions, cheat sheets, progress tracking.
Terminal-native.
Stays on your machine.

## What You Get

- Browse and practice the NeetCode 150 from the terminal.
- Start each problem from a local `starter.py`.
- Write private attempts in ignored `solution.py` files.
- Run local tests and track progress under `.walnut/`.
- Use cheat sheets and reference solutions when you need a nudge.

Only the first 14 problems are fully seeded with statements, local tests, and reference solutions right now: Arrays & Hashing plus Two Pointers.
The rest are roadmap entries with metadata, links, placeholder statements, and starters.

## Requirements

- Python 3.9+ with working `venv` and `pip`.
- On Debian/Ubuntu, install venv support with `sudo apt install python3-venv`.
- `bash` for the `setup` installer.
- macOS or Linux.
- Windows users should use WSL.
- Internet once during `./setup` to install `rich` and `textual`.
- Core practice is fully offline after setup.

## Quick Start

Install from the repo root:

```bash
./setup
```

Then open Walnut:

```bash
export PATH="$HOME/.local/bin:$PATH"
walnut
```

After setup, `walnut` can run from any directory.
The cloned repo stays the source of truth for the app, problem library, local progress, notes, and attempts.

In an interactive terminal, plain `walnut` opens the browse interface.
Use `walnut home` for the static dashboard, or `walnut tui` when you want to be explicit.

`./setup` creates `.venv/`, installs Walnut in editable mode, writes a `~/.local/bin/walnut` wrapper, pins that wrapper to this repo with `WALNUT_HOME`, and runs `doctor` plus `verify --all`.
It does not edit your shell profile by default.
It prints the one PATH line you can add yourself.
Pass `--modify-profile` if you want it to add that line to your shell profile.
Re-running setup is safe.

## Practice Flow

Open the browse interface:

```bash
walnut
```

From there:

1. Use `j/k` to move around the list.
2. Press `[` or `]` to switch between topics and the full problem list.
3. Press `enter` on a topic to drill in.
4. Highlight a problem and press `s` to start it.
5. Press `e` to open the selected `solution.py`.
6. Press `t` to run local tests.
7. Press `n` to open private notes.
8. Press `c` to open the cheat sheet.

You can also do the same flow with direct commands:

```bash
walnut topics
walnut list arrays-and-hashing
walnut show 3
walnut pick 3
```

Write your answer in the generated `solution.py` file:

```text
problems/01-arrays-and-hashing/03-two-sum/solution.py
```

Run it locally:

```bash
walnut test 3 --perf
```

Use a dry run when you do not want to update progress:

```bash
walnut run 3 --perf
```

## Useful Commands

| What you need | Command |
| --- | --- |
| Check setup | `walnut doctor` |
| Show topics | `walnut topics` |
| List a topic | `walnut list two-pointers` |
| Read a problem | `walnut show 3` |
| Start solving | `walnut pick 3` |
| Open solution in editor | `walnut edit 3` |
| Run tests | `walnut test 3 --perf` |
| Get next hint | `walnut hint 3` |
| Show reference solution | `walnut solution 3` |
| Pick the next unsolved problem | `walnut next` |
| Reset local attempt/progress for a problem | `walnut reset 3` |
| Print private notes path | `walnut notes 3` |
| Open private notes in editor | `walnut notes 3 --open` |
| Open a cheat sheet | `walnut cheat 3` |
| Print official links | `walnut open-official 3 --print` |
| Verify seeded solutions | `walnut verify --all --plain` |

## Terminal UI

```bash
walnut
```

`walnut tui` opens the same interface explicitly.

Key shortcuts:

```text
j/k       move
[/]       switch tabs
enter     open a topic
s         start the selected problem
e         open selected solution.py
t         run local tests
r         reset the active timer
n         open notes
c         open the cheat sheet
esc       go back one layer
/         filter
q         quit
```

If you prefer another shell or pane, run tests there with `walnut test <id> --perf`.
The TUI picks up the latest progress within a second.

## Recommended Tmux Workflow

Walnut is designed around a multi-pane terminal workflow.
Tmux is the recommended setup, but it is not required.
Ghostty tabs, iTerm panes, or any setup with separate terminal windows work too.

The layout I use is:

```text
walnut
  home    runs `walnut`
  editor  opens the selected solution.py when I press e
  notes   opens the selected notes.md when I press n
```

Create that layout manually:

```bash
tmux new-session -d -s walnut -n home -c "$PWD"
tmux new-window -t walnut -n editor -c "$PWD"
tmux new-window -t walnut -n notes -c "$PWD"
tmux send-keys -t walnut:home 'walnut' C-m
tmux attach -t walnut
```

The session is auto-detected and the target window names default to `editor` and `notes`.
The `WALNUT_TMUX_*` variables are only needed if your session or window names differ from that layout:

```bash
WALNUT_TMUX_SESSION=walnut \
WALNUT_TMUX_EDITOR_WINDOW=editor \
WALNUT_TMUX_NOTES_WINDOW=notes \
walnut
```

Inside that setup, `e` sends the selected `solution.py` to the `editor` window, and `n` sends the selected `notes.md` to the `notes` window.
The tmux integration expects `nvim` to be available, or an already-running `vim`, `vi`, or `nvim` in the target window.
Without tmux, those keys show the file path so you can open it however you like.

## What Stays Local

Your practice work is intentionally ignored by git:

```text
**/solution.py
**/notes.md
.walnut/
```

That means your attempts, notes, timers, and progress stay on your machine.
A fresh clone starts clean.

## Cheat Sheets

Per-topic cheat sheets live in `docs/cheatsheets/`.
They cover all 18 roadmap topics plus `python-stdlib` and `complexity`.

```bash
walnut cheat --list
walnut cheat arrays-and-hashing
walnut cheat python
walnut cheat complexity
```

## If `walnut` Is Not Found

See the full PATH fix in [Quickstart](docs/QUICKSTART.md#if-walnut-is-not-found).

## More Docs

- [Quickstart](docs/QUICKSTART.md)
- [Repo guide](docs/REPO_GUIDE.md)

## Content Note

`walnut sync-roadmap` refreshes public roadmap metadata only: titles, topic labels, difficulty, LeetCode IDs, and links.
It does not copy LeetCode or NeetCode statements, explanations, videos, or solution text.

This project links to LeetCode and follows the NeetCode 150 ordering, but the included statements, test cases, and reference solutions are original.
