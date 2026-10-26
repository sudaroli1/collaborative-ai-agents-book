"""Runs one design on one trip request and saves everything as JSON.
Used by run_all.py; you do not need to run it directly."""
import argparse, json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from trace_listener import TraceRecorder
from rail_tools import TOOL_LOG

ap = argparse.ArgumentParser()
for a in ("--design", "--request", "--out"):
    ap.add_argument(a, required=True)
a = ap.parse_args()

rec = TraceRecorder()
t0, err, answer, tasks, state = time.time(), None, None, [], None
try:
    if a.design == "workflow":
        from workflow4 import TripWorkflow
        flow = TripWorkflow()
        answer = flow.kickoff(inputs={"request": a.request})
        state = flow.state.model_dump()
    else:
        from designs4 import DESIGNS
        result = DESIGNS[a.design](a.request).kickoff(
            inputs={"request": a.request})
        answer = result.raw
        tasks = [t.raw for t in result.tasks_output]
except Exception as e:  # failures are results too
    err = f"{type(e).__name__}: {e}"
time.sleep(0.5)


def last(key):
    found = re.findall(key + r":\**\s*\**(\d{5}|NONE)", str(answer or ""),
                       re.I)
    return found[-1].upper() if found else None


ev = rec.events
json.dump({"design": a.design, "request": a.request, "answer": answer,
           "outbound": last("OUTBOUND"), "return": last("RETURN"),
           "state": state, "task_outputs": tasks, "error": err,
           "seconds": round(time.time() - t0, 1), "tool_calls": TOOL_LOG,
           "llm_calls": sum(1 for e in ev if e["event"] == "llm_call"),
           "tokens": sum((e.get("usage") or {}).get("total_tokens", 0)
                         for e in ev if e["event"] == "llm_call"),
           "trace": ev},
          open(a.out, "w", encoding="utf-8"), indent=2,
          ensure_ascii=False, default=str)
