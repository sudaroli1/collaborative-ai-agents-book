"""Listing 4-4. Coordination by code: a Flow that plans both journeys."""
import json, re
from pydantic import BaseModel
from crewai.flow.flow import Flow, start, listen
from team4 import llm
from rail_tools import search_trains
from rules4 import choose_train

ASK = ("Extract the two journeys in this request as JSON: "
       '{"outbound": {...}, "return": {...}}, each with keys origin, '
       "destination, day, time_of_day (morning, afternoon, evening, "
       "night or empty) and window (true/false). If the return day or "
       "time is not given, leave it empty. Reply with JSON only.\n"
       "Request: ")


class TripState(BaseModel):
    request: str = ""
    legs: dict = {}
    found: dict = {}


class TripWorkflow(Flow[TripState]):
    @start()
    def understand(self):                     # the model extracts
        reply = llm.call([{"role": "user",
                           "content": ASK + self.state.request}])
        self.state.legs = json.loads(
            re.search(r"\{.*\}", reply, re.S).group(0))

    @listen(understand)
    def plan(self):                           # code searches, chooses
        for name in ("outbound", "return"):
            leg = self.state.legs.get(name) or {}
            text = search_trains.run(origin=str(leg.get("origin", "")),
                                     destination=str(leg.get("destination",
                                                             "")),
                                     day=str(leg.get("day", "")))
            lines = text.splitlines()
            train = choose_train(lines, str(leg.get("time_of_day") or ""),
                                 bool(leg.get("window")))
            self.state.found[name] = {"train": train, "line": next(
                (l for l in lines if l.startswith(train)), "")}

    @listen(plan)
    def reply(self):                          # the model writes
        f = self.state.found
        text = llm.call([{"role": "user", "content": (
            "Write a two-sentence itinerary for a traveller who asked: '"
            + self.state.request + "'. Outbound: "
            + (f["outbound"]["line"] or "no suitable train") + ". Return: "
            + (f["return"]["line"] or "no suitable train")
            + ". Do not add any other train.")}])
        return (text.strip() + "\nOUTBOUND: " + f["outbound"]["train"]
                + "\nRETURN: " + f["return"]["train"])
