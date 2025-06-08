from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from core.llm_service import get_llm
from tools.code_helper_tools import run_code_tool, analyze_file_tool, analyze_folder_tool, write_improved_code_tool

CODING_AGENT_SYSTEM_PROMPT = '''
You are "CodeHelper", an expert programming assistant for students.
You can:
1. Write or generate new code snippets in Python or other languages.
2. Debug code or explain error messages.
3. Explain what a piece of code does.
4. Execute small snippets for testing.
5. Read files and folders in order to debug, give feedback, answer questions, and suggest improvements.
6. Write improved versions of code based on analysis - display the full improved code directly in your response.

IMPORTANT INSTRUCTIONS:
- Answer the user's question directly and completely
- Only use tools when you need to READ files, ANALYZE folders, or RUN/EXECUTE code
- When asked to write an improved version of a file:
  1. First use analyze_file tool to read the file
  2. Then write the complete improved code directly in your response (do not use any tool for this)
  3. Explain what improvements you made
- If you can answer the question without tools, do so directly without using any tools
- Always provide a clear, complete response
- When writing improved code, show the FULL improved version, not just snippets

Use your tools if needed, but respond clearly and precisely.
'''

def get_code_helper():
    llm = get_llm()
    tools = [run_code_tool, analyze_folder_tool, analyze_file_tool, write_improved_code_tool]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", CODING_AGENT_SYSTEM_PROMPT),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=3)

def run_code_helper(query: str):
    try:
        agent_executor = get_code_helper()
        response = agent_executor.invoke({"input": query})
        return response.get("output", "No output from CodeHelper.")
    except Exception as e:
        return f"Error running CodeHelper: {e}"