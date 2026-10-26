"""Listing 2-2. The tasks: recommend, then check."""
from crewai import Task
from agents import nova, rin

FORMAT = ("End with one line in exactly this form: "
          "RECOMMENDATION: <train number> (or RECOMMENDATION: NONE)")


def recommend_task(agent=nova, guardrail=None):
    return Task(
        description=("The traveller says: '{request}'. Find suitable "
                     "trains and recommend one. Do not book anything."),
        expected_output=("A short recommendation with the train number, "
                         "times and window-seat availability. " + FORMAT),
        agent=agent, guardrail=guardrail,
    )


def check_task(recommend, agent=rin):
    return Task(
        description=("The traveller says: '{request}'. Check the "
                     "recommendation you have been given against the "
                     "timetable. Confirm it if it is right; otherwise "
                     "replace it with the correct train, or NONE."),
        expected_output=("One sentence saying whether the recommendation "
                         "was correct and why. " + FORMAT),
        agent=agent, context=[recommend],
    )
