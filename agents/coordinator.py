def route_query(query: str, agent_name: str):
    """Routes a query to the specified agent."""
    if agent_name == "studybuddy":
        from .study_buddy_rag import run_study_buddy
        return run_study_buddy(query)
    elif agent_name == "codehelper":
        from .code_helper import run_code_helper
        return run_code_helper(query)
    elif agent_name == "scholarscout":
        from .scholar_scout import run_scholar_scout
        return run_scholar_scout(query)
    else:
        return f"Error: Unknown agent '{agent_name}'. Cannot route query."