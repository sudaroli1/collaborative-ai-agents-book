"""Runs every experiment in Chapter 4 and saves the results in ./results.

Usage (in this folder, with the .venv312 environment active):
    python run_all.py --quick   # one trip per design, about 10 minutes
    python run_all.py           # full experiment, about 75 minutes
"""
import argparse, json, os, platform, subprocess, sys, time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "results"
ENV = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
           NO_COLOR="1", CREWAI_TRACING_ENABLED="false",
           CREWAI_DISABLE_TELEMETRY="true", OTEL_SDK_DISABLED="true")
URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
SMALL = "llama3.2:3b"


def log(msg):
    print(msg, flush=True)
    with open(OUT / "run_log.txt", "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")


def run(args, console, env=ENV, timeout=1200):
    try:
        with open(OUT / console, "w", encoding="utf-8") as c:
            subprocess.run([sys.executable] + args, cwd=HERE, env=env,
                           stdout=c, stderr=subprocess.STDOUT,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        log(f"    timed out: {' '.join(args)}")


def models():
    tags = json.load(urllib.request.urlopen(URL + "/api/tags", timeout=5))
    return [m["name"] for m in tags.get("models", [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    try:
        have = models()
    except Exception as e:
        sys.exit(f"Cannot reach Ollama at {URL} ({e}). Start Ollama.")
    import crewai
    trips = json.load(open(HERE / "trips.json", encoding="utf-8"))
    if a.quick:
        trips = trips[:1]
    env = {"python": sys.version.split()[0], "crewai": crewai.__version__,
           "os": platform.platform(), "quick": a.quick, "models": have,
           "started": time.strftime("%Y-%m-%d %H:%M:%S")}

    # A. Six ways to coordinate the same job (Sections 4.1 and 4.2)
    designs = ["workflow", "single", "pipeline_text",
               "pipeline_structured", "parallel", "managed"]
    n = 0
    for d in designs:
        for t in trips:
            n += 1
            log(f"[A{n}] {d}: {t['id']}")
            run(["runner4.py", "--design", d, "--request", t["text"],
                 "--out", str(OUT / f"{d}_{t['id']}.json")],
                f"{d}_{t['id']}_console.txt")

    # B. A2A: publish the trip planner and use it (Section 4.3)
    log("[B] A2A server and client")
    srv_log = open(OUT / "a2a_server_console.txt", "w", encoding="utf-8")
    server = subprocess.Popen([sys.executable, "a2a_server4.py"], cwd=HERE,
                              env=ENV, stdout=srv_log,
                              stderr=subprocess.STDOUT)
    try:
        for _ in range(60):                  # wait for the Agent Card
            try:
                urllib.request.urlopen("http://localhost:9999/.well-known/"
                                       "agent-card.json", timeout=2)
                break
            except Exception:
                time.sleep(1)
        run(["a2a_client4.py", str(OUT / "a2a.json")],
            "a2a_client_console.txt")
    finally:
        server.terminate()
        srv_log.close()

    # C. Tests as quality gates (Section 4.4)
    log("[C1] unit tests")
    run(["-m", "pytest", "-m", "not llm", "-v"], "tests_unit.txt")
    if not a.quick:
        log("[C2] evaluation tests with llama3.1:8b")
        run(["-m", "pytest", "-m", "llm", "-v", "-s"], "tests_llm_8b.txt")
        if any(m.startswith(SMALL) for m in have):
            log(f"[C3] evaluation tests with {SMALL}")
            run(["-m", "pytest", "-m", "llm", "-v", "-s"],
                "tests_llm_3b.txt", env=dict(ENV, BOOK_MODEL=SMALL))
        else:
            log(f"[C3] skipped: run 'ollama pull {SMALL}' to include it")
    env["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(env, open(OUT / "environment.json", "w"), indent=2)
    log("All done. Tell Claude the Chapter 4 results are ready.")


if __name__ == "__main__":
    main()
