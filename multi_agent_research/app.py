"""app.py - Streamlit user interface."""
import streamlit as st

from config import check_api_keys
from workflow import build_workflow

# Friendly names shown in the progress area
AGENT_LABELS = {
    "research_agent": "Research Agent",
    "analysis_agent": "Analysis Agent",
    "writer_agent": "Writer Agent",
}

st.set_page_config(page_title="Multi-Agent Research Assistant", page_icon="🔎")
st.title("Multi-Agent Research Assistant")
st.write("Enter a topic and a team of AI agents will research it and write a report.")

topic = st.text_input("Research topic", placeholder="The Future of Artificial Intelligence")

if st.button("Generate Report"):
    missing_keys = check_api_keys()

    if missing_keys:
        st.error(f"Missing API keys in your .env file: {', '.join(missing_keys)}")
    elif not topic.strip():
        st.warning("Please enter a research topic.")
    else:
        workflow = build_workflow()
        final_state = {}  # we collect everything the agents return here

        with st.status("Agents are working...", expanded=True) as status:
            st.write("Supervisor received the topic.")

            # stream() gives us one update every time a node (agent) finishes
            for step in workflow.stream({"topic": topic.strip()}, stream_mode="updates"):
                for node_name, output in step.items():
                    final_state.update(output)

                    if node_name == "supervisor":
                        next_agent = output["next_agent"]
                        if next_agent == "FINISH":
                            st.write("Supervisor: all tasks are finished.")
                        else:
                            st.write(f"Supervisor is calling the {AGENT_LABELS[next_agent]}...")
                    elif "error" in output:
                        st.write(f"{AGENT_LABELS[node_name]} failed.")
                    else:
                        st.write(f"{AGENT_LABELS[node_name]} finished.")

            if final_state.get("error"):
                status.update(label="Something went wrong", state="error")
            else:
                status.update(label="Report is ready!", state="complete", expanded=False)

        # Show the result
        if final_state.get("error"):
            st.error(final_state["error"])
        else:
            st.divider()
            st.markdown(final_state["final_report"])
            st.download_button("Download report (.md)", final_state["final_report"],
                               file_name="research_report.md")

            with st.expander("Research Agent output"):
                st.markdown(final_state["research_results"])
            with st.expander("Analysis Agent output"):
                st.markdown(final_state["analysis"])
