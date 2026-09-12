#!/usr/bin/env python3
"""
Typing Speed Test — a small terminal app that measures your typing
speed (WPM) and accuracy against a random quote, and keeps a local
history of your results so you can track improvement over time.

Usage:
    python main.py            # run a test
    python main.py --stats    # show your personal stats / history
    python main.py --reset    # clear saved history
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from quotes import QUOTES

HISTORY_FILE = Path(__file__).parent / "history.json"

# ANSI colors (work in most modern terminals, including Windows Terminal)
GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


@dataclass
class Result:
    timestamp: str
    wpm: float
    accuracy: float
    duration_seconds: float
    quote_length: int


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def save_result(result: Result) -> None:
    history = load_history()
    history.append(asdict(result))
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def compute_accuracy(target: str, typed: str) -> float:
    """Percentage of characters typed correctly, position by position."""
    if not target:
        return 0.0
    correct = sum(1 for t, u in zip(target, typed) if t == u)
    # Penalize length mismatches (missing or extra characters)
    longest = max(len(target), len(typed))
    return (correct / longest) * 100 if longest else 0.0


def render_diff(target: str, typed: str) -> str:
    """Return the typed text with wrong characters highlighted in red."""
    out = []
    for i, ch in enumerate(typed):
        if i < len(target) and ch == target[i]:
            out.append(f"{GREEN}{ch}{RESET}")
        else:
            out.append(f"{RED}{ch}{RESET}")
    return "".join(out)


def run_test() -> None:
    quote = random.choice(QUOTES)
    print(f"\n{BOLD}Type the following sentence as fast and accurately as you can.{RESET}")
    print(f"{DIM}Press Enter when done.{RESET}\n")
    print(f"{BOLD}{quote}{RESET}\n")

    input(f"{DIM}Press Enter to start...{RESET}")
    start = time.perf_counter()
    typed = input("> ")
    end = time.perf_counter()

    duration = end - start
    if duration <= 0:
        duration = 0.01  # guard against instant/empty submissions

    word_count = len(quote.split())
    wpm = (word_count / duration) * 60
    accuracy = compute_accuracy(quote, typed)

    print(f"\n{render_diff(quote, typed)}\n")
    print(f"{BOLD}Time:{RESET}     {duration:.2f}s")
    print(f"{BOLD}WPM:{RESET}      {wpm:.1f}")
    print(f"{BOLD}Accuracy:{RESET} {accuracy:.1f}%")

    result = Result(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        wpm=round(wpm, 1),
        accuracy=round(accuracy, 1),
        duration_seconds=round(duration, 2),
        quote_length=len(quote),
    )
    save_result(result)

    history = load_history()
    if len(history) > 1:
        best_wpm = max(h["wpm"] for h in history)
        avg_wpm = statistics.mean(h["wpm"] for h in history)
        print(f"\n{DIM}Personal best: {best_wpm:.1f} WPM   |   Average: {avg_wpm:.1f} WPM   |   Runs: {len(history)}{RESET}")


def show_stats() -> None:
    history = load_history()
    if not history:
        print("No history yet — run a test first with: python main.py")
        return

    wpms = [h["wpm"] for h in history]
    accs = [h["accuracy"] for h in history]

    print(f"\n{BOLD}Typing Test Stats{RESET}")
    print(f"Runs:          {len(history)}")
    print(f"Best WPM:      {max(wpms):.1f}")
    print(f"Average WPM:   {statistics.mean(wpms):.1f}")
    print(f"Average Acc:   {statistics.mean(accs):.1f}%")
    print(f"\n{DIM}Last 5 runs:{RESET}")
    for h in history[-5:]:
        print(f"  {h['timestamp']}  —  {h['wpm']:.1f} WPM  —  {h['accuracy']:.1f}% accuracy")


def reset_history() -> None:
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
        print("History cleared.")
    else:
        print("No history to clear.")


def main() -> None:
    parser = argparse.ArgumentParser(description="A terminal typing speed test.")
    parser.add_argument("--stats", action="store_true", help="show your stats and history")
    parser.add_argument("--reset", action="store_true", help="clear saved history")
    args = parser.parse_args()

    if args.stats:
        show_stats()
    elif args.reset:
        reset_history()
    else:
        run_test()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted. Bye!")
        sys.exit(0)
