"""Listing 4-6. Three ways to use a remote A2A agent: read its Agent
Card, send it a message, and let a CrewAI agent delegate to it.
Start a2a_server4.py first, in another window."""
import json, sys, time, uuid
import httpx
from crewai import Agent, Crew, Task
from crewai.a2a.config import A2AClientConfig
from team4 import llm

BASE = "http://localhost:9999"
CARD = BASE + "/.well-known/agent-card.json"
TRIP = ("Bengaluru to Mysuru on Saturday morning and back on Sunday "
        "evening, window seats both ways.")
out = {}

# 1. Discovery: anyone can read what the agent offers
card = httpx.get(CARD).json()
print("Agent:", card["name"], "-", card["description"])
for skill in card["skills"]:
    print("  skill:", skill["name"], "-", skill["description"])
out["card"] = card

# 2. A plain JSON-RPC message: no agent framework needed
t0 = time.time()
reply = httpx.post(BASE + "/", timeout=300, json={
    "jsonrpc": "2.0", "id": 1, "method": "message/send",
    "params": {"message": {"role": "user", "messageId": uuid.uuid4().hex,
                           "parts": [{"kind": "text", "text": TRIP}]}}})
answer = reply.json()["result"]["parts"][0]["text"]
print(f"\nDirect reply ({time.time() - t0:.0f} s):\n{answer}")
out["direct"] = {"seconds": round(time.time() - t0, 1),
                 "request": TRIP, "reply": reply.json()}

# 3. A CrewAI agent that may delegate to the remote agent
assistant = Agent(
    role="Personal Assistant",
    goal="Look after Meera's travel arrangements",
    backstory=("You help Meera with her diary and travel. For train "
               "journeys you use specialist agents when available."),
    llm=llm, verbose=True,
    a2a=A2AClientConfig(endpoint=CARD, timeout=300, max_turns=3))
task = Task(description=("Meera says: '" + TRIP + "' Arrange her trains."),
            expected_output=("Her itinerary, ending with 'OUTBOUND: "
                             "<train or NONE>' and 'RETURN: <train or "
                             "NONE>'."), agent=assistant)
t0 = time.time()
try:
    result = Crew(agents=[assistant], tasks=[task]).kickoff().raw
except Exception as e:                      # failures are results too
    result = f"ERROR {type(e).__name__}: {e}"
print(f"\nDelegated reply ({time.time() - t0:.0f} s):\n{result}")
out["delegated"] = {"seconds": round(time.time() - t0, 1),
                    "reply": result}
if len(sys.argv) > 1:                        # run_all.py saves the record
    json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=2,
              ensure_ascii=False, default=str)
