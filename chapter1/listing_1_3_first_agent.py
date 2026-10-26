"""Listings 1-3 and 1-4. Our first agent: Nova, a rail travel assistant."""
from crewai import Agent, Task, Crew, Process, LLM
from config import MODEL, OLLAMA_URL
from rail_tools import search_trains

# Listing 1-3: the brain and the agent
llm = LLM(model=f"ollama/{MODEL}", base_url=OLLAMA_URL, temperature=0)

nova = Agent(
    role="Rail Travel Assistant",
    goal=("Find the best train for the traveller's request "
          "using real timetable data"),
    backstory=("You help busy people plan train journeys in Karnataka. "
               "You never guess train times: you always check the "
               "timetable tool, and you say clearly when no suitable "
               "train exists."),
    tools=[search_trains],
    llm=llm,
    max_iter=5,      # at most five think-act-observe cycles
    verbose=True,
)

# Listing 1-4: the task and the crew
plan_trip = Task(
    description=("The traveller says: '{request}'. Find suitable trains "
                 "and recommend one. Do not book or pay for anything."),
    expected_output=("A short recommendation naming the train number, "
                     "departure and arrival times and window-seat "
                     "availability, followed by the question "
                     "'Shall I go ahead and book it?'"),
    agent=nova,
)

crew = Crew(agents=[nova], tasks=[plan_trip],
            process=Process.sequential, verbose=True)

if __name__ == "__main__":
    result = crew.kickoff(inputs={
        "request": "Book me a train to Mysuru from Bengaluru for "
                   "Saturday morning, window seat please."})
    print("\nFINAL ANSWER:\n", result.raw)
