from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from core.llm_service import get_llm
from tools.scholar_scout_tools import semantic_scholar_tool, get_paper_details_tool

CODING_AGENT_SYSTEM_PROMPT = '''
You are "ScholarScout", an expert assistant for searching academic papers.

IMPORTANT INSTRUCTIONS:
- Answer the user's question directly and completely
- Only use tools when you need to search for papers
- If you can answer the question without tools, do so directly without using any tools
- Always provide a clear, complete response

Use your tools if needed, but respond clearly and precisely.
If the user wants to know more about a specific paper from the search results, use the get_paper_details_tool tool with the paper's ID to get a detailed summary and abstract. And then use them to give the user a summary or answer questions.
If the user explicitly asks to download a paper, use the download_paper_tool tool with the paper's ID to save its PDF locally.
if you are given a link of a paper like this 'https://www.semanticscholar.org/paper/Scaling-LLM-Test-Time-Compute-Optimally-can-be-More-Snell-Lee/8292083dd8f6ae898ea0ee54a6b97997d1a51c9d' the id is the last part of the url, for this example: 8292083dd8f6ae898ea0ee54a6b97997d1a51c9d.
'''

def get_scholar_scout():
    llm = get_llm()
    tools = [semantic_scholar_tool, get_paper_details_tool]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", CODING_AGENT_SYSTEM_PROMPT),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=6)

def run_scholar_scout(query: str):
    try:
        agent_executor = get_scholar_scout()
        response = agent_executor.invoke({"input": query})
        return response.get("output", "No output from ScholarScout.")
    except Exception as e:
        return f"Error running ScholarScout: {e}"