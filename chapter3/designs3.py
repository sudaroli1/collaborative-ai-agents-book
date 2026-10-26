"""Listing 3-4. The designs compared in Chapter 3."""
from crewai import Agent, Crew, Task, Process
from agents3 import nova, llm, recommend_task, check_task
from guardrail3 import booking_guardrail
from knowledge3 import search_passenger_guide, GUIDE
from memory3 import remember_preference, recall_preferences
from rail_tools import search_trains


def checked_v2(request):                  # 3.3: the repaired checker
    rec = recommend_task()
    return Crew(agents=[nova], tasks=[rec, check_task(rec)],
                process=Process.sequential)


def guarded_v2(request):                  # 3.3: the stronger guardrail
    t = recommend_task(guardrail=booking_guardrail(request))
    return Crew(agents=[nova], tasks=[t])


def helper(knowledge):                    # 3.2: three ways to know rules
    extra = {"none": "",
             "full": "\n\nThe complete passenger guide:\n" + GUIDE,
             "tool": ""}[knowledge]
    tools = [search_passenger_guide] if knowledge == "tool" else []
    agent = Agent(role="Passenger Help Desk",
                  goal="Answer travellers' questions about Deccan Rail",
                  backstory=("You answer questions about Deccan Rail rules "
                             "accurately and briefly. If you do not know "
                             "a rule, say so." + extra),
                  tools=tools, llm=llm, max_iter=4, verbose=True)
    task = Task(description="A traveller asks: '{request}'",
                expected_output="A short, accurate answer.", agent=agent)
    return Crew(agents=[agent], tasks=[task])


def booker(memory):                       # 3.2: with or without memory
    tools = [search_trains]
    if memory:
        tools += [recall_preferences, remember_preference]
    agent = Agent(role="Rail Travel Assistant",
                  goal=("Find the best train for the traveller using "
                        "real timetable data"),
                  backstory=("You plan train journeys in Karnataka. You "
                             "always check the timetable tool. "
                             + ("You always recall the traveller's saved "
                                "preferences first, and you save any new "
                                "lasting preference they tell you."
                                if memory else "")),
                  tools=tools, llm=llm, max_iter=6, verbose=True)
    task = Task(description=("The traveller says: '{request}'. Help them. "
                             "Do not book anything."),
                expected_output=("A short reply. If you recommend a train, "
                                 "end with RECOMMENDATION: <train number>, "
                                 "or RECOMMENDATION: NONE."),
                agent=agent)
    return Crew(agents=[agent], tasks=[task])


DESIGNS = {
    "checked_v2": checked_v2, "guarded_v2": guarded_v2,
    "guide_none": lambda r: helper("none"),
    "guide_full": lambda r: helper("full"),
    "guide_tool": lambda r: helper("tool"),
    "memory_off": lambda r: booker(False),
    "memory_on": lambda r: booker(True),
}
