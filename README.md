# Multi-Agent Research Assistant

An educational multi-agent system: type a topic and get a structured research report.
Built with **LangGraph**, **LangChain + Groq**, **Tavily Search** and **Streamlit**.

## Architecture

One **Supervisor** controls three **Worker** agents through a shared state.

```
                 ┌────────────┐
   topic ──────▶ │ Supervisor │ ──────▶ final report
                 └─────┬──────┘
        ┌──────────────┼───────────────┐
        ▼              ▼               ▼
  Research Agent  Analysis Agent  Writer Agent
  (Tavily + LLM)      (LLM)          (LLM)
```

| Agent | Job |
|---|---|
| Supervisor | Reads the shared state, decides which worker runs next, stops when done |
| Research Agent | Searches the web with Tavily and summarizes the findings |
| Analysis Agent | Finds insights, advantages, disadvantages and challenges |
| Writer Agent | Writes the report: Introduction, Main Findings, Analysis, Conclusion |

Workflow: `START → Supervisor → Research → Supervisor → Analysis → Supervisor → Writer → Supervisor → END`

## Project structure

| File | Purpose |
|---|---|
| `config.py` | Loads `.env`, checks API keys, creates the Groq LLM |
| `agents.py` | The 4 agents as simple functions |
| `workflow.py` | Shared state + LangGraph `StateGraph` |
| `app.py` | Streamlit interface |
| `requirements.txt` | Dependencies |
| `.env.example` | Template for your API keys |

## Setup (Windows PowerShell)

```powershell
cd multi_agent_research

# 1. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file, then open it and paste your API keys
Copy-Item .env.example .env
notepad .env
```

If PowerShell blocks the activation script, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Get free API keys from [Groq Console](https://console.groq.com/keys) and [Tavily](https://app.tavily.com/).

## Run

```powershell
streamlit run app.py
```

Open http://localhost:8501, enter a topic such as *The Future of Artificial Intelligence*, and click **Generate Report**.

## Error handling

Each worker wraps its work in `try/except`. On failure it writes an `error` message to the shared state; the Supervisor then stops the workflow and the UI shows the error. Missing API keys are detected before any agent runs.

## Ideas to extend

- Let the Supervisor use an LLM to choose the next worker.
- Add a review loop where the Supervisor sends the report back for improvement.
