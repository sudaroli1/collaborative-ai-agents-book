"""Reads the OUTBOUND and RETURN lines of an answer (not printed)."""
import re


def read_trains(answer):
    def last(key):
        found = re.findall(key + r":\s*(\d{5}|NONE)", answer)
        return found[-1] if found else None
    return last("OUTBOUND"), last("RETURN")
