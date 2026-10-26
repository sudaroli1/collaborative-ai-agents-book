"""Runs only the third version of the checker (Listing 3-8) on the
twelve test requests, about 12 minutes. Other results are kept.

Usage (in this folder, with the .venv312 environment active):
    python run_v3.py
"""
import json, os, sys, time, urllib.request
from run_all import run, log, OUT, HERE

OUT.mkdir(exist_ok=True)
url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
try:
    urllib.request.urlopen(url + "/api/tags", timeout=5)
except Exception as e:
    sys.exit(f"Cannot reach Ollama at {url} ({e}). Start Ollama.")
reqs = json.load(open(HERE / "requests.json", encoding="utf-8"))
if "--quick" in sys.argv:
    reqs = reqs[:1]
for i, r in enumerate(reqs, 1):
    log(f"[{i}] checked_v3: {r['id']}")
    run("checked_v3", r["id"], r["text"])
log("All done. Tell Claude the checked_v3 results are ready.")
