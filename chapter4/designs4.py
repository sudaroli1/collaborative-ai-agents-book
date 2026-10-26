"""Listing 4-2. Five ways to coordinate the same job."""
from crewai import Crew, Task, Process
from team4 import (nova, kenji, aiko, sora, researcher, leg_task,
                   itinerary_task, FINAL)


def single(request):                      # one agent does everything
    task = Task(description=("The traveller says: '{request}'. Plan both "
                             "journeys. Do not book."),
                expected_output="A short itinerary. " + FINAL, agent=nova)
    return Crew(agents=[nova], tasks=[task])


def pipeline(structured):                 # researcher, then writer
    legs = [leg_task("outbound", structured),
            leg_task("return", structured)]
    return Crew(agents=[kenji, aiko], tasks=legs + [itinerary_task(legs)],
                process=Process.sequential)


def parallel(request):                    # both legs at the same time,
    a, b = researcher(), researcher()     # so two researchers are needed
    legs = [leg_task("outbound", True, parallel=True, agent=a),
            leg_task("return", True, parallel=True, agent=b)]
    return Crew(agents=[a, b, aiko], tasks=legs + [itinerary_task(legs)],
                process=Process.sequential)


def managed(request):                     # a manager decides
    task = Task(description=("The traveller says: '{request}'. Plan both "
                             "journeys. Do not book."),
                expected_output="A short itinerary. " + FINAL)
    return Crew(agents=[kenji, aiko], tasks=[task], manager_agent=sora,
                process=Process.hierarchical)


DESIGNS = {"single": single,
           "pipeline_text": lambda r: pipeline(False),
           "pipeline_structured": lambda r: pipeline(True),
           "parallel": parallel, "managed": managed}
