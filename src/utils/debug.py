"""Host utilities for debugging."""

import sys


def print_and_flush(text):
    if "num_chars_printed" not in globals():
        global num_chars_printed
        num_chars_printed = 0

    overwrite_chars = " " * (num_chars_printed - len(text))
    sys.stdout.write(text + "\r")
    sys.stdout.flush()
    num_chars_printed = len(text)
