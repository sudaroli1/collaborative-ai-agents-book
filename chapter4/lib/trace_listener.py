"""Listing 2-5. A trace recorder: what happened, who did it, and when."""
import time
from crewai.events import BaseEventListener
from crewai.events.types.agent_events import (
    AgentExecutionStartedEvent, AgentExecutionCompletedEvent)
from crewai.events.types.tool_usage_events import (
    ToolUsageStartedEvent, ToolUsageFinishedEvent)
from crewai.events.types.llm_events import LLMCallCompletedEvent
from crewai.events.types.llm_guardrail_events import (
    LLMGuardrailCompletedEvent)


class TraceRecorder(BaseEventListener):
    def __init__(self):
        self.events, self.t0 = [], time.time()
        super().__init__()

    def log(self, kind, **data):
        self.events.append({"t": round(time.time() - self.t0, 1),
                            "event": kind, **data})

    def setup_listeners(self, bus):
        @bus.on(AgentExecutionStartedEvent)
        def started(source, e):
            self.log("agent_started", agent=e.agent.role)

        @bus.on(ToolUsageStartedEvent)
        def tool(source, e):
            self.log("tool_called", agent=e.agent_role,
                     tool=e.tool_name, args=e.tool_args)

        @bus.on(ToolUsageFinishedEvent)
        def tool_done(source, e):
            self.log("tool_result", agent=e.agent_role,
                     output=str(e.output)[:400])

        @bus.on(LLMCallCompletedEvent)
        def llm(source, e):
            self.log("llm_call", usage=e.usage)

        @bus.on(LLMGuardrailCompletedEvent)
        def guard(source, e):
            self.log("guardrail", success=e.success, error=e.error,
                     retry=e.retry_count)

        @bus.on(AgentExecutionCompletedEvent)
        def done(source, e):
            self.log("agent_finished", agent=e.agent.role,
                     output=str(e.output)[:600])
