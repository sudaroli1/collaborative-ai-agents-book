"""Listing 4-1. The booking rules as plain functions, shared by the
workflow, the A2A server and the tests."""
import re

SLOTS = {"morning": (5, 12), "afternoon": (12, 17),
         "evening": (17, 21), "night": (20, 24)}


def departs(line):
    return int(re.search(r"departs (\d\d):", line).group(1))


def choose_train(lines, time_of_day="", window=False):
    """The first train (in time order) that fits, or NONE."""
    slot = SLOTS.get((time_of_day or "").strip().lower())
    for line in lines:
        if not line[:5].isdigit():
            continue
        if slot and not slot[0] <= departs(line) < slot[1]:
            continue
        if window and line.endswith("window seats free: 0"):
            continue
        return line[:5]
    return "NONE"
