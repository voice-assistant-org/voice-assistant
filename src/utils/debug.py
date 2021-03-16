"""Host utilities for debugging."""

import sys

num_chars_printed = 0


def print_and_flush(text: str) -> None:
    """Print and flush."""
    global num_chars_printed
    overwrite_chars = " " * (num_chars_printed - len(text))
    sys.stdout.write(f"{text}{overwrite_chars}\r")
    sys.stdout.flush()
    num_chars_printed = len(text)
