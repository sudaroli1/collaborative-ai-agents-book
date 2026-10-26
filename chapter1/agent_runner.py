"""Runs the Listing 1-3/1-4 agent once and saves everything it did as JSON.
Used by run_all.py; you do not need to run it directly."""
import argparse, json, time
import listing_1_3_first_agent as L
from rail_tools import TOOL_LOG

ap = argparse.ArgumentParser()
ap.add_argument("--request", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()

t0 = time.time()
err = None
try:
    result = L.crew.kickoff(inputs={"request": a.request})
    answer = result.raw
    usage = result.token_usage.model_dump() if getattr(result, "token_usage", None) else None
except Exception as e:  # record failures too: they are results
    answer, usage, err = None, None, f"{type(e).__name__}: {e}"
json.dump({"request": a.request, "answer": answer, "error": err,
           "seconds": round(time.time() - t0, 1), "tool_calls": TOOL_LOG,
           "token_usage": usage}, open(a.out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
