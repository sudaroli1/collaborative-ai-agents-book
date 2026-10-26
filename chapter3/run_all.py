"""Runs every experiment in Chapter 3 and saves the results in ./results.

Usage (in this folder, with the .venv312 environment active):
    python run_all.py --quick   # one request per experiment, ~8 minutes
    python run_all.py           # full experiment, about 40 minutes
"""
import argparse, json, os, platform, subprocess, sys, time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "results"
MEM = HERE / "data" / "memory.json"
ENV = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
           NO_COLOR="1", CREWAI_TRACING_ENABLED="false",
           CREWAI_DISABLE_TELEMETRY="true", OTEL_SDK_DISABLED="true")


def log(msg):
    print(msg, flush=True)
    with open(OUT / "run_log.txt", "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")


def run(design, rid, text):
    stem = OUT / f"{design}_{rid}"
    try:
        with open(f"{stem}_console.txt", "w", encoding="utf-8") as c:
            subprocess.run([sys.executable, "runner3.py", "--design", design,
                            "--request", text, "--out", f"{stem}.json"],
                           cwd=HERE, env=ENV, stdout=c,
                           stderr=subprocess.STDOUT, timeout=900)
    except subprocess.TimeoutExpired:
        log(f"    timed out: {design} {rid}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    try:
        urllib.request.urlopen(url + "/api/tags", timeout=5)
    except Exception as e:
        sys.exit(f"Cannot reach Ollama at {url} ({e}). Start Ollama.")
    import crewai
    reqs = json.load(open(HERE / "requests.json", encoding="utf-8"))
    pol = json.load(open(HERE / "policy_questions.json", encoding="utf-8"))
    mem = json.load(open(HERE / "memory_requests.json", encoding="utf-8"))
    cut = (lambda xs: xs[:1]) if a.quick else (lambda xs: xs)
    plan = []
    for d in ("workflow", "guarded_v2", "checked_v2"):
        plan += [(d, r["id"], r["text"]) for r in cut(reqs)]
    for d in ("guide_none", "guide_full", "guide_tool"):
        plan += [(d, q["id"], q["text"]) for q in cut(pol)]
    plan += [("memory_off", r["id"], r["text"]) for r in cut(mem["requests"])]
    env = {"python": sys.version.split()[0], "crewai": crewai.__version__,
           "os": platform.platform(), "quick": a.quick,
           "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    log(f"CrewAI {crewai.__version__} | {len(plan) + 1 + len(cut(mem['requests']))} runs")
    for i, (d, rid, text) in enumerate(plan, 1):
        log(f"[{i}] {d}: {rid}")
        run(d, rid, text)
    # memory: one teaching conversation, then new conversations that recall
    if MEM.exists():
        MEM.unlink()
    log("[memory] teaching session")
    run("memory_on", "TEACH", mem["teach"])
    for r in cut(mem["requests"]):
        log(f"[memory] memory_on: {r['id']}")
        run("memory_on", r["id"], r["text"])
    env["memory_file"] = MEM.read_text() if MEM.exists() else None
    env["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(env, open(OUT / "environment.json", "w"), indent=2)
    log("All done. Tell Claude the Chapter 3 results are ready.")


if __name__ == "__main__":
    main()
