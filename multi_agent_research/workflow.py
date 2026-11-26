"""workflow.py - builds the LangGraph workflow (Supervisor + 3 Workers)."""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from agents import analysis_agent, research_agent, supervisor_agent, writer_agent


class ResearchState(TypedDict, total=False):
    """Shared state: every agent reads from it and writes to it."""
    topic: str              # input from the user
    research_results: str   # written by the Research Agent
    analysis: str           # written by the Analysis Agent
    final_report: str       # written by the Writer Agent
    next_agent: str         # decided by the Supervisor
    error: str              # set by any agent if something fails


def route_from_supervisor(state):
    """Conditional edge: send the flow to the worker the supervisor chose."""
    if state["next_agent"] == "FINISH":
        return END
    return state["next_agent"]


def build_workflow():
    """Create and compile the graph.

    START -> supervisor -> (research | analysis | writer | END)
    Every worker always returns to the supervisor.
    """
    graph = StateGraph(ResearchState)

    # Add the 4 agents as nodes
    graph.add_node("supervisor", supervisor_agent)
    graph.add_node("research_agent", research_agent)
    graph.add_node("analysis_agent", analysis_agent)
    graph.add_node("writer_agent", writer_agent)

    # The workflow always starts at the supervisor
    graph.add_edge(START, "supervisor")

    # The supervisor decides which node runs next (or ends the workflow)
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "research_agent": "research_agent",
            "analysis_agent": "analysis_agent",
            "writer_agent": "writer_agent",
            END: END,
        },
    )

    # Workers report back to the supervisor
    graph.add_edge("research_agent", "supervisor")
    graph.add_edge("analysis_agent", "supervisor")
    graph.add_edge("writer_agent", "supervisor")

    return graph.compile()
