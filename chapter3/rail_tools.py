"""From Chapter 1 (Listing 1-2). Searches a (fictional) train timetable.

The data in data/timetable.csv is invented for this book. Every call is
recorded in TOOL_LOG so that we can show exactly what the agent did.
"""
import csv
import time
from pathlib import Path

from crewai.tools import tool

DATA = Path(__file__).parent / "data" / "timetable.csv"
TOOL_LOG = []  # one entry per tool call, filled at run time


@tool("search_trains")
def search_trains(origin: str, destination: str, day: str) -> str:
    """Find trains between two cities on a given day of the week.
    Returns departure and arrival times and free window seats."""
    def same(a, b):
        return a.strip().lower() == b.strip().lower()

    with open(DATA, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)
                if same(r["origin"], origin)
                and same(r["destination"], destination)
                and same(r["day"], day)]
    if not rows:
        result = f"No trains found from {origin} to {destination} on {day}."
    else:
        result = "\n".join(
            f"{r['train_no']} {r['train_name']}: departs {r['departs']}, "
            f"arrives {r['arrives']}, "
            f"window seats free: {r['window_seats_free']}"
            for r in rows)
    TOOL_LOG.append({
        "time": time.strftime("%H:%M:%S"), "tool": "search_trains",
        "args": {"origin": origin, "destination": destination, "day": day},
        "result": result})
    return result
