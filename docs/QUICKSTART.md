# Walnut Quickstart

This is the shortest path from a fresh clone to solving a problem.

## 1. Setup

From the repo root:

```bash
./setup
```

The setup script does four things:

- checks that Python 3.9+ is available
- creates a local `.venv/` and installs the normal CLI and TUI dependencies there
- makes the `walnut` command available on your shell `PATH` when needed
- runs `walnut doctor` and `walnut verify --all`

If it updates your shell profile, open a new terminal or run the command it prints,
usually:

```bash
source ~/.zshrc
```

## 2. Browse

```bash
walnut
walnut topics
walnut list arrays-and-hashing
walnut show 3
```

In an interactive terminal, plain `walnut` opens the TUI.
Use `walnut home` for the static dashboard.

## 3. Solve

Start Two Sum:

```bash
walnut pick 3
```

Edit the created file:

```text
problems/01-arrays-and-hashing/03-two-sum/solution.py
```

Run tests:

```bash
walnut test 3 --perf
```

Use a dry run when you do not want to mutate progress:

```bash
walnut run 3 --perf
```

Add `--plain` to any command when you want simpler copy/paste output.

## 4. Keep Notes

```bash
walnut notes 3
```

This creates a private ignored `notes.md` beside the problem.

## 5. Open Official Links

Print the official URLs:

```bash
walnut open-official 3 --site leetcode --print
walnut open-official 3 --site neetcode --print
```

Open in your browser:

```bash
walnut open-official 3 --site leetcode
```

## 6. Verify The Repo

```bash
make smoke
```

Or without `make`:

```bash
python3 -m unittest discover -s tests
walnut verify --all --plain
```

## If `walnut` Is Not Found

Run:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

To make it permanent in zsh:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

You can always use the fallback from the repo root:

```bash
python3 -m walnut.cli doctor
```
