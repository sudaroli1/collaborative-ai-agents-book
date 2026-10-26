"""Listing 3-6. A stronger guardrail: seats and the time of day."""
import re
from rail_tools import TOOL_LOG

SLOTS = {"morning": (5, 12), "afternoon": (12, 17),
         "evening": (17, 21), "night": (20, 24)}


def booking_guardrail(request):
    text = request.lower()
    wants_window = "window" in text
    slot = next((s for s in SLOTS if s in text), None)

    def check(output):
        m = re.search(r"RECOMMENDATION:\s*(\d{5}|NONE)", output.raw)
        if not m:
            return (False, "End with 'RECOMMENDATION: <train> or NONE'.")
        train = m.group(1)
        if train == "NONE":
            return (True, output.raw)
        seen = "\n".join(c["result"] for c in TOOL_LOG).splitlines()
        line = next((l for l in seen if l.startswith(train)), None)
        if line is None:
            return (False, f"Train {train} is not in the timetable "
                           "results you received. Use the tool.")
        if wants_window and line.endswith("window seats free: 0"):
            return (False, f"Train {train} has no free window seats.")
        hour = int(re.search(r"departs (\d\d):", line).group(1))
        if slot and not SLOTS[slot][0] <= hour < SLOTS[slot][1]:
            return (False, f"Train {train} does not leave in the "
                           f"{slot}. Recommend a {slot} train, or NONE.")
        return (True, output.raw)

    return check
