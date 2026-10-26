"""Listing 3-1. The same job as a workflow: code decides, model talks."""
import json, re
from pydantic import BaseModel
from crewai.flow.flow import Flow, start, listen
from agents3 import llm
from rail_tools import search_trains
from guardrail3 import SLOTS


class Trip(BaseModel):
    request: str = ""
    origin: str = ""
    destination: str = ""
    day: str = ""
    time_of_day: str = ""
    window: bool = False
    candidates: list = []
    choice: str = "NONE"


class RailWorkflow(Flow[Trip]):
    @start()
    def understand(self):                 # step 1: the model extracts
        reply = llm.call([{"role": "user", "content": (
            "Extract the journey from this request as JSON with keys "
            "origin, destination, day, time_of_day (morning, afternoon, "
            "evening, night or empty) and window (true/false). Reply "
            "with JSON only.\nRequest: " + self.state.request)}])
        data = json.loads(re.search(r"\{.*\}", reply, re.S).group(0))
        for key in ("origin", "destination", "day", "time_of_day"):
            setattr(self.state, key, str(data.get(key) or ""))
        self.state.window = bool(data.get("window"))

    @listen(understand)
    def search(self):                     # step 2: code searches
        s = self.state
        result = search_trains.run(origin=s.origin,
                                   destination=s.destination, day=s.day)
        s.candidates = [l for l in result.splitlines() if l[:5].isdigit()]

    @listen(search)
    def choose(self):                     # step 3: code applies the rules
        s = self.state
        for line in s.candidates:          # timetable is in time order
            hour = int(re.search(r"departs (\d\d):", line).group(1))
            slot = SLOTS.get(s.time_of_day.lower())
            if slot and not slot[0] <= hour < slot[1]:
                continue
            if s.window and line.endswith("window seats free: 0"):
                continue
            s.choice = line[:5]
            break

    @listen(choose)
    def reply(self):                      # step 4: the model writes
        s = self.state
        fact = next((l for l in s.candidates if l.startswith(s.choice)),
                    "no train matches the request")
        text = llm.call([{"role": "user", "content": (
            "Write one friendly sentence to a traveller who asked: '"
            + s.request + "'. The answer is: " + fact + ". Do not add "
            "any other train or detail.")}])
        return text.strip() + "\nRECOMMENDATION: " + s.choice
