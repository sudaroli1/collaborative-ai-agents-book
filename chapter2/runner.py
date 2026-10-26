"""Runs one design on one request and saves everything as JSON.
Used by run_all.py; you do not need to run it directly."""
import argparse, json, re, time
from trace_listener import TraceRecorder
from crews import DESIGNS
from rail_tools import TOOL_LOG

ap = argparse.ArgumentParser()
for a in ("--design", "--request", "--out"):
    ap.add_argument(a, required=True)
a = ap.parse_args()

rec = TraceRecorder()
crew = DESIGNS[a.design](a.request)
t0, err, answer, usage, tasks = time.time(), None, None, None, []
try:
    result = crew.kickoff(inputs={"request": a.request})
    answer = result.raw
    usage = result.token_usage.model_dump() if result.token_usage else None
    tasks = [t.raw for t in result.tasks_output]
except Exception as e:  # failures are results too
    err = f"{type(e).__name__}: {e}"
time.sleep(0.5)  # let the event bus deliver the last events
found = re.findall(r"RECOMMENDATION:\s*(\d{5}|NONE)", answer or "")
json.dump({"design": a.design, "request": a.request, "answer": answer,
           "recommendation": found[-1] if found else None,
           "task_outputs": tasks, "error": err,
           "seconds": round(time.time() - t0, 1), "tool_calls": TOOL_LOG,
           "token_usage": usage, "trace": rec.events},
          open(a.out, "w", encoding="utf-8"), indent=2,
          ensure_ascii=False, default=str)
