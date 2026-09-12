# Typing Speed Test

A small terminal app that measures your typing speed (WPM) and accuracy
against a random quote, and tracks your history locally so you can watch
yourself improve.

No dependencies — just the Python standard library.

## Usage

```bash
python main.py            # run a test
python main.py --stats    # view your stats and recent history
python main.py --reset    # clear saved history
```

## How it works

1. A random quote is picked from `quotes.py`.
2. You hit Enter to start the clock, type the quote, and hit Enter again.
3. The app compares what you typed to the original character by character,
   highlights mistakes in red, and reports your **words per minute** and
   **accuracy**.
4. Results are appended to `history.json` (git-ignored) so `--stats` can
   show your best and average WPM over time.

## Ideas for extending it(tomorrow)

- Add more quotes (or load them from a file/API)
- Add difficulty modes (code snippets, numbers, punctuation-heavy text)
- Live character-by-character feedback while typing (would need a
  library like `curses` or `textual` instead of a single `input()` call)
- A `--time` mode: type as many words as possible in N seconds
