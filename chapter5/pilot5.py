"""Listing 5-1. A pilot measurement: accuracy, speed and token use of
the trip planner (Listing 4-4) on 36 varied requests.
Usage: python pilot5.py llama3.1:8b"""
import json, os, statistics, sys, time
from pathlib import Path
HERE = Path(__file__).parent
MODEL = os.environ["BOOK_MODEL"] = sys.argv[1]     # before the imports
sys.path[:0] = [str(HERE.parent / "chapter4"),
                str(HERE.parent / "chapter4" / "lib")]
from trace_listener import TraceRecorder
from workflow4 import TripWorkflow
from runner_util import read_trains

trace, rows = TraceRecorder(), []
for r in json.load(open(HERE / "pilot_requests.json")):
    start, t0 = len(trace.events), time.time()
    try:
        answer = str(TripWorkflow().kickoff(inputs={"request": r["text"]}))
    except Exception as e:                   # a failure is a result
        answer = f"ERROR {type(e).__name__}: {e}"
    out, ret = read_trains(answer)
    calls = [e for e in trace.events[start:] if e["event"] == "llm_call"]
    rows.append({**r, "got_outbound": out, "got_return": ret,
                 "correct": (out, ret) == (r["outbound"], r["return"]),
                 "seconds": round(time.time() - t0, 1),
                 "tokens": sum((e.get("usage") or {}).get("total_tokens", 0)
                               for e in calls), "answer": answer})
    print(r["id"], out, ret, "ok" if rows[-1]["correct"] else "WRONG")

secs = sorted(x["seconds"] for x in rows)
summary = {"model": MODEL, "requests": len(rows),
           "correct": sum(x["correct"] for x in rows),
           "median_seconds": statistics.median(secs),
           "p90_seconds": secs[int(0.9 * len(secs)) - 1],
           "mean_tokens": round(statistics.mean(x["tokens"] for x in rows))}
print(json.dumps(summary, indent=1))
(HERE / "results").mkdir(exist_ok=True)
json.dump({"summary": summary, "rows": rows}, open(
    HERE / "results" / f"pilot_{MODEL.replace(':', '_')}.json", "w",
    encoding="utf-8"), indent=1, ensure_ascii=False)
