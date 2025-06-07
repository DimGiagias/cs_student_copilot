from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.llm_service import get_llm
from tools.rag_tools import IndexDirectoryTool, QueryKnowledgeBaseTool

STUDY_BUDDY_SYSTEM_PROMPT = """
You are "StudyBuddy", an AI assistant that helps users interact with their personal knowledge base of course materials.
You have two main tools:
1. `index_document_directory`: To add documents from a folder to the knowledge base.
2. `query_knowledge_base`: To ask questions about the documents already in the knowledge base.

Your task is to choose the single best tool to respond to the user's request and then stop.- If the user wants to add new documents or create an index, use `index_document_directory`.
- If the user explicitly asks to 'index', 'add documents', or 'rebuild' the knowledge base, use the `index_document_directory` tool.
- For all other questions, assume the user is asking about the content of their documents and use the `query_knowledge_base` tool.
- Do not chain tool calls or perform additional actions unless explicitly asked to in a new request.
"""

def get_study_buddy_agent_executor():
    llm = get_llm()
    tools = [IndexDirectoryTool(), QueryKnowledgeBaseTool()]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", STUDY_BUDDY_SYSTEM_PROMPT),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=3)

def run_study_buddy(query: str):
    try:
        agent_executor = get_study_buddy_agent_executor()
        response = agent_executor.invoke({"input": query})
        return response.get("output", "No output from StudyBuddy.")
    except Exception as e:
        return f"Error running StudyBuddy: {e}"