"""Listing 4-2. The team: a researcher, a writer and a manager, and the
two ways they can hand work to each other (text or structured data)."""
from pydantic import BaseModel, Field
from crewai import Agent, Task, LLM
from config import MODEL, OLLAMA_URL
from rail_tools import search_trains

llm = LLM(model=f"ollama/{MODEL}", base_url=OLLAMA_URL, temperature=0)
FINAL = ("End with exactly two lines: 'OUTBOUND: <train number or "
         "NONE>' and 'RETURN: <train number or NONE>'.")


class Leg(BaseModel):                     # a structured hand-off
    origin: str
    destination: str
    day: str
    train: str = Field(description="Train number, or NONE")
    timetable_line: str = Field(description="Copied from the tool")
    reason: str


nova = Agent(role="Rail Travel Assistant",
             goal="Plan complete train journeys from real timetable data",
             backstory=("You plan journeys in Karnataka. You always check "
                        "the timetable tool and never guess."),
             tools=[search_trains], llm=llm, max_iter=6, verbose=True)


def researcher():                         # a fresh Kenji on each call
    return Agent(role="Rail Researcher",
                 goal="Find the right train for one journey",
                 backstory=("You search the timetable for one journey at "
                            "a time and pick the first train that fits the "
                            "day, the time of day and any window seat "
                            "request. If none fits, you say NONE."),
                 tools=[search_trains], llm=llm, max_iter=5, verbose=True)


kenji = researcher()

aiko = Agent(role="Itinerary Writer",
             goal="Turn colleagues' findings into a clear itinerary",
             backstory=("You write short, friendly itineraries. You use "
                        "only the trains your colleagues found."),
             llm=llm, verbose=True)

sora = Agent(role="Trip Manager",
             goal="Get the traveller a correct, complete itinerary",
             backstory=("You lead a researcher and a writer. You split the "
                        "work, delegate it and check the result."),
             llm=llm, allow_delegation=True, verbose=True)


def leg_task(journey, structured=False, parallel=False, agent=kenji):
    return Task(
        description=("The traveller says: '{request}'. Find the train for "
                     f"the {journey} journey only."),
        expected_output=("The chosen train for this journey with its "
                         "timetable line, or NONE if no train fits."),
        output_pydantic=Leg if structured else None,
        async_execution=parallel, agent=agent)


def itinerary_task(legs):
    return Task(
        description=("The traveller says: '{request}'. Write the "
                     "itinerary from your colleagues' findings."),
        expected_output="A short itinerary. " + FINAL,
        context=legs, agent=aiko)
