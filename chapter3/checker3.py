"""Listing 3-8. The checker, third version: evidence handed over in code,
no tools, a structured verdict, and the final decision taken in code."""
import re
from types import SimpleNamespace
from typing import Literal
from pydantic import BaseModel, Field
from crewai import Agent, Crew, Task
from agents3 import nova, llm, recommend_task
from rail_tools import TOOL_LOG

Mark = Literal["PASS", "FAIL", "NOT ASKED"]


class Verdict(BaseModel):                   # what Rin must return
    route: Mark
    day: Mark
    time_of_day: Mark
    window_seat: Mark
    evidence: str = Field(description="The timetable line you used")
    replacement: str = Field(description="If a criterion fails: the "
                             "number of a train that meets all, or NONE")


rin3 = Agent(
    role="Booking Checker",
    goal="Judge a train recommendation against four criteria",
    backstory=("You judge whether a recommended train meets the "
               "traveller's request on (1) route, (2) day, (3) time of "
               "day and (4) a free window seat. Mark a criterion NOT "
               "ASKED if the traveller did not mention it. You use only "
               "the timetable you are given. If the recommendation is "
               "NONE, mark every criterion PASS if no train in the "
               "timetable meets all of the traveller's conditions."),
    tools=[], llm=llm, verbose=True)          # no tools to misuse

verdict_task = Task(
    description=("The traveller says: '{request}'.\n"
                 "The complete timetable found:\n{timetable}\n"
                 "A colleague recommends:\n{recommendation}\n"
                 "Judge the recommendation against the four criteria."),
    expected_output=("Only a JSON object with the keys route, day, "
                     "time_of_day and window_seat (each PASS, FAIL or "
                     "NOT ASKED), evidence and replacement."),
    agent=rin3, output_pydantic=Verdict)


def last_train(text):
    found = re.findall(r"RECOMMENDATION:\s*(\d{5}|NONE)", text or "")
    return found[-1] if found else None


class CheckedV3:
    def kickoff(self, inputs):
        first = Crew(agents=[nova], tasks=[recommend_task()]).kickoff(
            inputs=inputs)                    # step 1: Nova recommends
        timetable = "\n".join(c["result"] for c in TOOL_LOG) or "None"
        try:                                  # step 2: Rin judges
            second = Crew(agents=[rin3], tasks=[verdict_task]).kickoff(
                inputs={**inputs, "timetable": timetable,
                        "recommendation": first.raw})
            v, raw, outs = second.pydantic, second.raw, second.tasks_output
        except Exception as e:                # no valid verdict
            v, raw, outs = None, f"No valid verdict ({e})", []
        choice = None                         # step 3: code decides
        if v is not None:
            marks = [v.route, v.day, v.time_of_day, v.window_seat]
            if "FAIL" not in marks:
                choice = last_train(first.raw)          # confirm
            else:
                found = re.findall(r"\d{5}", v.replacement)
                choice = found[0] if found else "NONE"  # replace, but
                if choice not in timetable:             # only with a
                    choice = "NONE"                     # real train
        return SimpleNamespace(raw=raw + f"\nRECOMMENDATION: {choice}",
                               token_usage=None,
                               tasks_output=first.tasks_output + outs)


def checked_v3(request):
    return CheckedV3()
