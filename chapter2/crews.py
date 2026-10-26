"""Listing 2-4. Four ways to organise the same work."""
from crewai import Crew, Process
from agents import nova, rin, llm
from tasks import recommend_task, check_task
from guardrail import window_seat_guardrail


def single(request):                      # Chapter 1 design
    return Crew(agents=[nova], tasks=[recommend_task()])


def guarded(request):                     # one agent + code guardrail
    t = recommend_task(guardrail=window_seat_guardrail(request))
    return Crew(agents=[nova], tasks=[t])


def checked(request):                     # two agents, in sequence
    rec = recommend_task()
    return Crew(agents=[nova, rin], tasks=[rec, check_task(rec)],
                process=Process.sequential)


def managed(request):                     # a manager delegates the work
    rec = recommend_task(agent=None)
    chk = check_task(rec, agent=None)
    return Crew(agents=[nova, rin], tasks=[rec, chk],
                process=Process.hierarchical, manager_llm=llm)


DESIGNS = {"single": single, "guarded": guarded,
           "checked": checked, "managed": managed}
