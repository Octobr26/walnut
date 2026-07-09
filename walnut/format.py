from __future__ import annotations

from typing import Any

from rich.text import Text

from . import progress as progress_mod


STATUS_ICONS = {"solved": ("✓", "green"), "attempted": ("●", "yellow"), "unsolved": ("○", "dim")}


def status_for(progress: dict[str, Any], slug: str) -> str:
    return progress.get("problems", {}).get(slug, {}).get("status", "unsolved")


def format_time(seconds: int | None) -> str:
    if seconds is None:
        return "--"
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}:{secs:02d}"


def target_for(problem: dict[str, Any], active: dict[str, Any] | None = None) -> int:
    if active and active.get("target_sec"):
        return int(active["target_sec"])
    return progress_mod.TARGET_TIMES.get(problem.get("difficulty", "Medium"), 1800)


def short(value: Any, limit: int = 220) -> str:
    text = repr(value)
    if len(text) <= limit:
        return text
    return text[: limit - 20] + " ... <truncated>"


def failure_by_case(result: Any) -> dict[int, Any]:
    return {failure.index: failure for failure in result.failures}


def progress_bar_core(
    done: int,
    total: int,
    *,
    width: int,
    filled_style: str,
    partial_style: str,
    empty_style: str = "dim",
    clamp_edges: bool = False,
) -> Text:
    total = max(total, 1)
    filled = round(width * min(done, total) / total)
    if clamp_edges and done > 0 and filled == 0:
        filled = 1
    if clamp_edges and done < total and filled == width:
        filled = width - 1
    style = filled_style if done >= total else partial_style
    text = Text()
    text.append("█" * filled, style=style)
    text.append("░" * (width - filled), style=empty_style)
    return text


def progress_text(done: int, total: int, width: int = 18) -> Text:
    return progress_bar_core(
        done,
        total,
        width=width,
        filled_style="green",
        partial_style="cyan",
    )


def progress_bar(done: int, total: int, width: int = 12) -> Text:
    return progress_bar_core(
        done,
        total,
        width=width,
        filled_style="green",
        partial_style="green",
        clamp_edges=True,
    )
