"""agents.py - the 4 agents: 1 Supervisor + 3 Workers.

Every agent is a plain function. It receives the shared state (a dict)
and returns a dict with only the keys it wants to update.
"""
from tavily import TavilyClient

from config import TAVILY_API_KEY, get_llm


def ask_llm(system_prompt, user_prompt):
    """Small helper: send a system + user prompt to the LLM, return the text."""
    llm = get_llm()
    response = llm.invoke([("system", system_prompt), ("human", user_prompt)])
    return response.content


# ---------------------------------------------------------------------------
# WORKER 1: Research Agent
# ---------------------------------------------------------------------------
def research_agent(state):
    """Search the web with Tavily, then summarize the key findings."""
    topic = state["topic"]
    try:
        # 1) Search the web
        client = TavilyClient(api_key=TAVILY_API_KEY)
        search = client.search(query=topic, max_results=5)
        results = search.get("results", [])
        if not results:
            return {"error": "Research Agent: Tavily returned no results."}

        # 2) Put the search results into one text block for the LLM
        raw_text = ""
        for item in results:
            raw_text += f"Title: {item['title']}\nURL: {item['url']}\n{item['content']}\n\n"

        # 3) Ask the LLM to summarize the most important findings
        summary = ask_llm(
            "You are a research assistant. Summarize the most important findings "
            "from the search results as clear bullet points. Use only the given information.",
            f"Topic: {topic}\n\nSearch results:\n{raw_text}",
        )

        # 4) Add the source links at the end
        sources = "\n".join(f"- {item['title']}: {item['url']}" for item in results)
        return {"research_results": f"{summary}\n\nSources:\n{sources}"}

    except Exception as error:
        return {"error": f"Research Agent failed: {error}"}


# ---------------------------------------------------------------------------
# WORKER 2: Analysis Agent
# ---------------------------------------------------------------------------
def analysis_agent(state):
    """Analyze the research results: insights, advantages, disadvantages, challenges."""
    try:
        analysis = ask_llm(
            "You are an analyst. Analyze the research and give a clear analysis with "
            "these sections: Key Insights, Advantages, Disadvantages, Challenges.",
            f"Topic: {state['topic']}\n\nResearch results:\n{state['research_results']}",
        )
        return {"analysis": analysis}

    except Exception as error:
        return {"error": f"Analysis Agent failed: {error}"}


# ---------------------------------------------------------------------------
# WORKER 3: Writer Agent
# ---------------------------------------------------------------------------
def writer_agent(state):
    """Write the final professional report from the research and the analysis."""
    try:
        report = ask_llm(
            "You are a professional report writer. Write a research report in Markdown "
            "with exactly these sections: Introduction, Main Findings, Analysis, Conclusion. "
            "Start with a title. Use a professional tone.",
            f"Topic: {state['topic']}\n\n"
            f"Research results:\n{state['research_results']}\n\n"
            f"Analysis:\n{state['analysis']}",
        )
        return {"final_report": report}

    except Exception as error:
        return {"error": f"Writer Agent failed: {error}"}


# ---------------------------------------------------------------------------
# SUPERVISOR: controls the workflow
# ---------------------------------------------------------------------------
def supervisor_agent(state):
    """Look at the shared state and decide which worker must run next.

    The state tells the supervisor how far the work has progressed:
      - no research yet   -> Research Agent
      - no analysis yet   -> Analysis Agent
      - no report yet     -> Writer Agent
      - everything ready  -> FINISH
    If any worker reported an error, the supervisor stops the workflow.
    """
    if state.get("error"):
        next_agent = "FINISH"
    elif not state.get("research_results"):
        next_agent = "research_agent"
    elif not state.get("analysis"):
        next_agent = "analysis_agent"
    elif not state.get("final_report"):
        next_agent = "writer_agent"
    else:
        next_agent = "FINISH"

    return {"next_agent": next_agent}
