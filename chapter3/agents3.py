"""Listing 3-5. Rin, repaired: explicit criteria, evidence, a default."""
from crewai import Agent, Task, LLM
from config import MODEL, OLLAMA_URL
from rail_tools import search_trains

llm = LLM(model=f"ollama/{MODEL}", base_url=OLLAMA_URL, temperature=0)
FORMAT = ("End with one line in exactly this form: "
          "RECOMMENDATION: <train number> (or RECOMMENDATION: NONE)")

nova = Agent(
    role="Rail Travel Assistant",
    goal=("Find the best train for the traveller's request "
          "using real timetable data"),
    backstory=("You help busy people plan train journeys in Karnataka. "
               "You never guess train times: you always check the "
               "timetable tool, and you say clearly when no suitable "
               "train exists."),
    tools=[search_trains], llm=llm, max_iter=5, verbose=True)

rin = Agent(
    role="Booking Checker",
    goal="Confirm correct recommendations and correct wrong ones",
    backstory=("You check recommendations against four criteria only: "
               "(1) the route, (2) the day, (3) the time of day asked "
               "for, and (4) at least one free window seat if the "
               "traveller wants one. You quote the timetable line you "
               "used. If all four criteria are met, you CONFIRM the "
               "recommendation unchanged. Only if a criterion fails do "
               "you replace it, with a train that meets all four, or "
               "with NONE."),
    tools=[search_trains], llm=llm, max_iter=5, verbose=True)


def recommend_task(guardrail=None):
    return Task(
        description=("The traveller says: '{request}'. Search the "
                     "timetable and recommend one train. Do not book."),
        expected_output=("The timetable line of the recommended train, "
                         "one sentence explaining why it fits the "
                         "request, then the final line. " + FORMAT),
        agent=nova, guardrail=guardrail)


def check_task(recommend):
    return Task(
        description=("The traveller says: '{request}'. A colleague's "
                     "recommendation and evidence are in your context. "
                     "Check them against your four criteria."),
        expected_output=("For each criterion, PASS or FAIL with the "
                         "timetable line as evidence; then CONFIRMED or "
                         "REPLACED. " + FORMAT),
        agent=rin, context=[recommend])
