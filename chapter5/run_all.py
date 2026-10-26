"""Runs the Chapter 5 pilot with both models; results go in ./results.

Usage (in this folder, with the .venv312 environment active):
    python run_all.py --quick   # 3 requests per model, about 3 minutes
    python run_all.py           # 36 requests per model, about 30 minutes
"""
import json, os, subprocess, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
ENV = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
           NO_COLOR="1", CREWAI_TRACING_ENABLED="false",
           CREWAI_DISABLE_TELEMETRY="true", OTEL_SDK_DISABLED="true")
URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
try:
    tags = json.load(urllib.request.urlopen(URL + "/api/tags", timeout=5))
except Exception as e:
    sys.exit(f"Cannot reach Ollama at {URL} ({e}). Start Ollama.")
have = [m["name"] for m in tags.get("models", [])]
(HERE / "results").mkdir(exist_ok=True)
subprocess.run([sys.executable, "make_requests5.py"], cwd=HERE, env=ENV)
if "--quick" in sys.argv:
    reqs = json.load(open(HERE / "pilot_requests.json"))
    json.dump(reqs[:3], open(HERE / "pilot_requests.json", "w"), indent=1)
for model in ("llama3.1:8b", "llama3.2:3b"):
    if not any(m.startswith(model) for m in have):
        print(f"Skipping {model}: run 'ollama pull {model}' to include it")
        continue
    print(time.strftime("%H:%M:%S"), "pilot with", model, flush=True)
    with open(HERE / "results" / f"console_{model.replace(':', '_')}.txt",
              "w", encoding="utf-8") as c:
        subprocess.run([sys.executable, "pilot5.py", model], cwd=HERE,
                       env=ENV, stdout=c, stderr=subprocess.STDOUT)
if "--quick" in sys.argv:                    # restore the full set
    subprocess.run([sys.executable, "make_requests5.py"], cwd=HERE, env=ENV)
print("All done. Tell Claude the Chapter 5 results are ready.")
