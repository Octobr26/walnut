# walnut

`walnut` is a small offline LeetCode practice CLI.
I made it so I could keep practicing on long flights, while traveling, or anytime I do not have Wi-Fi.

It gives you the NeetCode 150 roadmap, local problem files, starters, seeded reference solutions, a test runner, cheat sheets, and local progress tracking from the terminal.

## What You Get

- A terminal-first way to browse and practice the NeetCode 150.
- Local starters and tests for seeded problems.
- Cheat sheets for every roadmap topic.
- Private `solution.py`, `notes.md`, timers, and progress.
- No LeetCode login, browser, or Wi-Fi needed after setup.

## Quick Start

Install from the repo root:

```bash
./setup
```

Then open Walnut:

```bash
walnut
```

In an interactive terminal, plain `walnut` opens the browse interface.
Use `walnut home` for the static dashboard, or `walnut tui` when you want to be explicit.

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
r         reset the active problem
n         open notes
c         open the cheat sheet
esc       go back
/         filter
q         quit
```

If you prefer another shell or pane, run tests there with `walnut test <id> --perf`.
The TUI picks up the latest progress within a second.

## Tmux Workflow

Walnut works well with tmux, Ghostty tabs, iTerm panes, or any setup where you keep multiple terminal windows open.

The layout I use is:

```text
walnut
  home    runs `walnut`
  editor  opens the selected solution.py when I press e
  notes   opens the selected notes.md when I press n
```

My local `tm walnut` shortcut creates that session for me.
The important part is that the `home` window runs Walnut with these environment variables:

```bash
WALNUT_TMUX_SESSION=walnut \
WALNUT_TMUX_EDITOR_WINDOW=editor \
WALNUT_TMUX_NOTES_WINDOW=notes \
walnut
```

To make the same layout manually:

```bash
tmux new-session -d -s walnut -n home -c "$PWD"
tmux new-window -t walnut -n editor -c "$PWD"
tmux new-window -t walnut -n notes -c "$PWD"
tmux send-keys -t walnut:home 'WALNUT_TMUX_SESSION=walnut WALNUT_TMUX_EDITOR_WINDOW=editor WALNUT_TMUX_NOTES_WINDOW=notes walnut' C-m
tmux attach -t walnut
```

Inside that setup, `e` sends the selected `solution.py` to the `editor` window, and `n` sends the selected `notes.md` to the `notes` window.
Without tmux, those keys show the file path so you can open it however you like.

## What Stays Local

Your practice work is intentionally ignored by git:

```text
**/solution.py
**/notes.md
.walnut/
```

That means your attempts, notes, timers, progress, and local snapshots stay on your machine.
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

Add the local command directory to your shell path:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

For zsh, make it permanent:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

You can always use the package directly from the repo root:

```bash
python3 -m walnut.cli doctor
```

## More Docs

- [Quickstart](docs/QUICKSTART.md)
- [Repo guide](docs/REPO_GUIDE.md)

## Content Note

`walnut sync-roadmap` refreshes public roadmap metadata only: titles, topic labels, difficulty, LeetCode IDs, and links.
It does not copy LeetCode or NeetCode statements, explanations, videos, or solution text.

This project links to LeetCode and follows the NeetCode 150 ordering, but the included statements, test cases, and reference solutions are original.
