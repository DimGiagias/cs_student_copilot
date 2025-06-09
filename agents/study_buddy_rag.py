from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from core.llm_service import get_llm
from rag_components.rag_manager import RAGManager

class ToolChoice(BaseModel):
    tool_name: Literal["index_document_directory", "query_knowledge_base"] = Field(..., description="The name of the tool to use.")
    tool_input: str = Field(..., description="The input query or path for the chosen tool.")

ROUTE_PROMPT_TEMPLATE = """
You are an expert router. Your job is to analyze a user's request and decide which of two tools is appropriate to use. You must respond in a JSON format with the tool name and the correct input for that tool.

<TOOLS>
1. index_document_directory: Use this when the user asks to 'index', 'add', 'process', or 'rebuild' their knowledge base. The input should be ONLY the directory path. Example: './my_docs'
2. query_knowledge_base: Use this for any other case where the user is asking a question. The input should be the user's question itself.
</TOOLS>

User Request: {query}
"""

FINAL_ANSWER_PROMPT_TEMPLATE = """
You are a helpful AI assistant named StudyBuddy. Your task is to transform the raw output from a tool into a polished, final answer for the user.

Here is the user's original request:
"{original_query}"

Here is the raw output from the tool that was run:
"{tool_output}"

---

Now, based on the tool's output, formulate a final response following these rules:

1.  **If the tool's output contains an answer and a "Sources Used" section:**
    - First, present the main answer from the tool's output in a clear and well-written paragraph.
    - Then, add a "Sources" section at the end and list the file names from the "Sources Used" line. Use a bulleted list for the sources for easy readability.

2.  **If the tool's output is a success message about indexing files (e.g., contains 'Successfully created new index'):**
    - Rephrase this into a friendly and clear confirmation. For example, you could say: "Great! I've successfully processed the documents. Your knowledge base is now ready to be queried." or "I've finished indexing the directory and have added the new information to your knowledge base."

3.  **If the tool's output is an error or an "I don't know" response:**
    - Present that information clearly and politely to the user without adding extra information.

Final Polished Response:
"""

def get_route_chain():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(ROUTE_PROMPT_TEMPLATE)
    return prompt | llm.with_structured_output(ToolChoice)

rag_manager = RAGManager()

def execute_tool(tool_choice: ToolChoice) -> dict:
    if tool_choice.tool_name == "index_document_directory":
        path_str = tool_choice.tool_input.strip().replace("'", "").replace('"', '')
        force_re = "force recreate is set to true" in tool_choice.tool_input.lower()
        return {"tool_output": rag_manager.build_or_update_index(Path(path_str), force_recreate=force_re)}
    elif tool_choice.tool_name == "query_knowledge_base":
        return {"tool_output": rag_manager.query(tool_choice.tool_input)}
    else:
        return {"tool_output": "Error: Invalid tool chosen by router."}

def get_final_answer_chain():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(FINAL_ANSWER_PROMPT_TEMPLATE)
    return prompt | llm | StrOutputParser()

def run_study_buddy(query: str):
    try:
        route_chain = get_route_chain()
        final_answer_chain = get_final_answer_chain()

        full_chain = (
            {"chosen_tool": route_chain, "original_query": RunnablePassthrough()}
            | RunnableLambda(lambda x: {"tool_output": execute_tool(x["chosen_tool"])["tool_output"], "original_query": x["original_query"]["query"]})
            | final_answer_chain
        )
        return full_chain.invoke({"query": query})
    except Exception as e:
        return f"An error occurred in the StudyBuddy chain: {e}"
