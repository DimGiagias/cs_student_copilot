from pathlib import Path

from pydantic import BaseModel, Field
from langchain.tools import StructuredTool

class CodeInput(BaseModel):
    code: str = Field(description="The code to execute.")

def run_code(code: str) -> str:
    print(f"\n--- Code Execution Request ---\nCode to execute:\n```python\n{code}\n```")
    confirm = input("Do you want to execute this code? [y/N]: ").lower()
    
    if confirm != 'y':
        return "Execution cancelled by user."
    
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