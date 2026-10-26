"""Listing 2-3. A guardrail: a check written in code, not in prose."""
import re
from rail_tools import TOOL_LOG


def window_seat_guardrail(request):
    wants_window = "window" in request.lower()

    def check(output):
        m = re.search(r"RECOMMENDATION:\s*(\d{5}|NONE)", output.raw)
        if not m:
            return (False, "End with 'RECOMMENDATION: <train> or NONE'.")
        train = m.group(1)
        if train == "NONE":
            return (True, output.raw)
        seen = "\n".join(c["result"] for c in TOOL_LOG)
        line = next((l for l in seen.splitlines()
                     if l.startswith(train)), None)
        if line is None:
            return (False, f"Train {train} is not in any timetable "
                           "result you received. Use the tool.")
        if wants_window and line.endswith("window seats free: 0"):
            return (False, f"Train {train} has no free window seats. "
                           "Recommend a train with free window seats, "
                           "or NONE.")
        return (True, output.raw)

    return check
