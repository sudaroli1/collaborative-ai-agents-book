"""Runs every experiment in Chapter 2 and saves the results in ./results.

Usage (in this folder, with the .venv312 environment active):
    python run_all.py --quick   # 2 requests per design, about 8 minutes
    python run_all.py           # full experiment, about 45 minutes
"""
import argparse, json, os, platform, subprocess, sys, time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "results"
ENV = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
           NO_COLOR="1", CREWAI_TRACING_ENABLED="false",
           CREWAI_DISABLE_TELEMETRY="true", OTEL_SDK_DISABLED="true")
MANAGED_SUBSET = ["Q01", "Q02", "Q03", "Q04", "Q09", "Q11"]


def log(msg):
    print(msg, flush=True)
    with open(OUT / "run_log.txt", "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    try:
        tags = json.load(urllib.request.urlopen(url + "/api/tags",
                                                timeout=5))
    except Exception as e:
        sys.exit(f"Cannot reach Ollama at {url} ({e}). "
                 "Start the Ollama app and try again.")
    model = os.environ.get("BOOK_MODEL", "llama3.1:8b")
    have = [m["name"] for m in tags.get("models", [])]
    if model not in have:
        sys.exit(f"Model {model} not found. Run: ollama pull {model}")
    import crewai
    reqs = json.load(open(HERE / "requests.json", encoding="utf-8"))
    plan = []
    for design in ("single", "guarded", "checked", "managed"):
        chosen = [r for r in reqs
                  if design != "managed" or r["id"] in MANAGED_SUBSET]
        if a.quick:
            chosen = chosen[:2]
        plan += [(design, r) for r in chosen]
    env = {"model": model, "python": sys.version.split()[0],
           "crewai": crewai.__version__, "os": platform.platform(),
           "machine": platform.processor(), "quick": a.quick,
           "started": time.strftime("%Y-%m-%d %H:%M:%S"), "runs": len(plan)}
    json.dump(env, open(OUT / "environment.json", "w"), indent=2)
    log(f"Model {model} | CrewAI {crewai.__version__} | {len(plan)} runs")
    for i, (design, r) in enumerate(plan, 1):
        log(f"[{i}/{len(plan)}] {design}: {r['id']}")
        stem = OUT / f"{design}_{r['id']}"
        try:
            with open(f"{stem}_console.txt", "w", encoding="utf-8") as c:
                subprocess.run([sys.executable, "runner.py", "--design",
                                design, "--request", r["text"],
                                "--out", f"{stem}.json"], cwd=HERE,
                               env=ENV, stdout=c,
                               stderr=subprocess.STDOUT, timeout=900)
        except subprocess.TimeoutExpired:
            log(f"    timed out after 15 minutes: {design} {r['id']}")
    env["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(env, open(OUT / "environment.json", "w"), indent=2)
    log("All done. Tell Claude the Chapter 2 results are ready.")


if __name__ == "__main__":
    main()
