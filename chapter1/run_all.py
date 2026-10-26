"""Runs every experiment in Chapter 1 and saves the results in ./results.

Usage (Anaconda Prompt, in this folder):
    python run_all.py            # 3 repeats per request (about 15-40 minutes on a laptop)
    python run_all.py --repeats 1   # quick check
"""
import argparse, json, os, platform, subprocess, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "results"; OUT.mkdir(exist_ok=True)
ENV = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", NO_COLOR="1",
           CREWAI_TRACING_ENABLED="false", CREWAI_DISABLE_TELEMETRY="true", OTEL_SDK_DISABLED="true")
PREFERRED = ["llama3.1:8b", "qwen2.5:7b", "qwen3:8b", "llama3.2:3b", "llama3.2", "mistral-nemo", "mistral"]

REQUESTS = {  # request -> what a correct answer must contain (checked against data/timetable.csv)
    "R1_saturday": "Book me a train to Mysuru from Bengaluru for Saturday morning, window seat please.",
    "R2_sunday": "I need to get from Bengaluru to Mysuru on Sunday morning and I want a window seat.",
    "R3_no_route": "Find me a train from Bengaluru to Hubballi on Saturday.",
}
BARE_Q = {
    "R1_saturday": "Which trains can I take from Bengaluru to Mysuru on Saturday morning, and which one has a free window seat?",
    "R2_sunday": "Which trains go from Bengaluru to Mysuru on Sunday morning, and which one has a free window seat?",
    "R3_no_route": "Which train can I take from Bengaluru to Hubballi on Saturday?",
}

def log(msg):
    print(msg, flush=True)
    with open(OUT / "run_log.txt", "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--repeats", type=int, default=3); a = ap.parse_args()
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    try:
        tags = json.load(urllib.request.urlopen(url + "/api/tags", timeout=5))
    except Exception as e:
        sys.exit(f"Cannot reach Ollama at {url} ({e}). Start the Ollama app and try again.")
    have = [m["name"] for m in tags.get("models", [])]
    model = os.environ.get("BOOK_MODEL") or next((p for p in PREFERRED if p in have or p + ":latest" in have), None)
    if not model:
        sys.exit(f"Installed models: {have}. Please run:  ollama pull llama3.1:8b   and try again.")
    ENV["BOOK_MODEL"] = model
    import crewai
    env = {"model": model, "installed_models": have, "python": sys.version.split()[0],
           "crewai": crewai.__version__, "os": platform.platform(), "machine": platform.processor(),
           "started": time.strftime("%Y-%m-%d %H:%M:%S"), "repeats": a.repeats}
    json.dump(env, open(OUT / "environment.json", "w"), indent=2)
    log(f"Model: {model} | CrewAI {crewai.__version__} | Python {env['python']}")

    # Experiment A: the bare language model (Listing 1-1), once per question
    for key, q in BARE_Q.items():
        log(f"[A] bare model: {key}")
        code = ("import json,sys,time; from listing_1_1_chatbot import llm; t=time.time(); "
                f"r=llm.call([{{'role':'user','content':{q!r}}}]); "
                "json.dump({'question':%r,'answer':r,'seconds':round(time.time()-t,1)},"
                "open(sys.argv[1],'w',encoding='utf-8'),indent=2,ensure_ascii=False)" % q)
        subprocess.run([sys.executable, "-c", code, str(OUT / f"A_bare_{key}.json")], cwd=HERE, env=ENV)

    # Experiment B: the agent (Listings 1-3, 1-4), repeated
    for i in range(1, a.repeats + 1):
        for key, req in REQUESTS.items():
            log(f"[B] agent run {i}/{a.repeats}: {key}")
            with open(OUT / f"B_agent_{key}_run{i}_console.txt", "w", encoding="utf-8") as con:
                subprocess.run([sys.executable, "agent_runner.py", "--request", req,
                                "--out", str(OUT / f"B_agent_{key}_run{i}.json")],
                               cwd=HERE, env=ENV, stdout=con, stderr=subprocess.STDOUT)
    env["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(env, open(OUT / "environment.json", "w"), indent=2)
    log("All done. Results are in the 'results' folder. Tell Claude they are ready.")

if __name__ == "__main__":
    main()
