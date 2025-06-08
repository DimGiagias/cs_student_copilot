from core.llm_service import get_llm
from langchain.tools import Tool, StructuredTool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from pathlib import Path

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

class CodeInput(BaseModel):
    code: str = Field(description="The code to execute.")

def run_code(code: str) -> str:
    try:
        local_vars = {}
        exec(code, {}, local_vars)
        return str(local_vars) or "Executed successfully."
    except Exception as e:
        return f"Error: {e}"
    
run_code_tool = StructuredTool(
    name="run_code",
    func=run_code,
    description="Executes code provided as a string input.",
    args_schema=CodeInput
)
    

class FileInput(BaseModel):
    path: str = Field(description="Path to the file to analyze.")

def analyze_file(path: str):
    try:
        file_path = Path(path)
        if not file_path.exists() or not file_path.is_file():
            return f"File not found: {path}"

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return f"Here is the content of {path}:\n\n{content}"
    
    except Exception as e:
        return f"Error reading file: {e}"
    
analyze_file_tool = StructuredTool(
    name="analyze_file",
    description="Reads and summarizes the content of a file, optionally giving feedback.",
    args_schema=FileInput,
    func=analyze_file,
)
    
class FolderInput(BaseModel):
    folder_path: str = Field(description="Path to folder of code files.")

def analyze_folder(folder_path: str):
    try:
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return f"Folder not found: {folder_path}"

        results = []
        for file in folder.rglob("*.py"):  
            try:
                content = file.read_text(encoding='utf-8')
                results.append(f"\nFile: {file.name}\n{content}\n")
            except Exception as e:
                results.append(f"\nFile: {file.name}\nError reading: {e}\n")

        return "\n".join(results) 
    
    except Exception as e:
        return f"Error reading folder: {e}"
    
analyze_folder_tool = StructuredTool(
    name="analyze_folder",
    description="Reads and summarizes the content of a folder, optionally giving feedback for each file.",
    args_schema=FolderInput,
    func=analyze_folder,
)

class ImprovedCodeInput(BaseModel):
    original_code: str = Field(description="The original code to improve")
    improvements: str = Field(description="Description of improvements to make")

def write_improved_code(original_code: str, improvements: str) -> str:
    try:
        return f"Improved code based on: {improvements}\n\nOriginal code:\n{original_code}"
    except Exception as e:
        return f"Error generating improved code: {e}"

write_improved_code_tool = StructuredTool(
    name="write_improved_code",
    description="Generates an improved version of code based on analysis and suggestions. Does not save files, only displays the improved code.",
    args_schema=ImprovedCodeInput,
    func=write_improved_code,   
)


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