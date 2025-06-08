from core.llm_service import get_llm
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

CODING_AGENT_SYSTEM_PROMPT = '''
You are "CodeHelper", an exprert programming assistant for students.
You can:
1. Write or generate new code snippets in Python or other languages.
2. Debug code or explain error messages.
3. Explain what a piece of code does.
4. Execute small Python snippets for testing.

Use your tools if needed, but respond clearly and precisely.
'''

def run_python_code(code: str) -> str:
    try:
        local_vars = {}
        exec(code, {}, local_vars)
        return str(local_vars) or "Executed successfully."
    except Exception as e:
        return f"Error: {e}"

run_python_tool = Tool(
    name="run_python",
    func=run_python_code,
    description="Executes Python code provided as a string input."
)

def get_code_helper():
    llm = get_llm()
    tools = [run_python_tool]
    
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