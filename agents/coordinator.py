def route_query(query: str, agent_name: str):
    """Routes a query to the specified agent."""
    if agent_name == "studybuddy":
        from .study_buddy_rag import run_study_buddy_chain
        return run_study_buddy_chain(query)
    else:
        return f"Error: Unknown agent '{agent_name}'. Cannot route query."