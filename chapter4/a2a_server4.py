"""Listing 4-5. Publishing the trip planner as an A2A agent.

Run it in its own window:  python a2a_server4.py
Its Agent Card is then at http://localhost:9999/.well-known/agent-card.json
"""
import asyncio
import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils import new_agent_text_message
from workflow4 import TripWorkflow

card = AgentCard(                            # how others discover us
    name="Deccan Rail Trip Planner",
    description=("Plans return train journeys in Karnataka from the "
                 "live Deccan Rail timetable."),
    url="http://localhost:9999/", version="1.0.0",
    default_input_modes=["text/plain"], default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(streaming=True),
    skills=[AgentSkill(
        id="plan_return_trip", name="Plan a return trip",
        description=("Given a request in plain English, finds the "
                     "outbound and return trains, respecting time of day "
                     "and window-seat wishes."),
        tags=["rail", "travel", "timetable"],
        examples=["Bengaluru to Mysuru on Saturday morning, back on "
                  "Sunday evening, window seats."])])


def plan(text):
    return TripWorkflow().kickoff(inputs={"request": text})


class TripExecutor(AgentExecutor):           # what happens on a request
    async def execute(self, context: RequestContext, queue: EventQueue):
        answer = await asyncio.to_thread(plan, context.get_user_input())
        await queue.enqueue_event(new_agent_text_message(str(answer)))

    async def cancel(self, context: RequestContext, queue: EventQueue):
        raise NotImplementedError("Cancelling is not supported")


app = A2AStarletteApplication(
    agent_card=card,
    http_handler=DefaultRequestHandler(agent_executor=TripExecutor(),
                                       task_store=InMemoryTaskStore()))

if __name__ == "__main__":
    uvicorn.run(app.build(), host="127.0.0.1", port=9999)
