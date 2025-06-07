from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from pathlib import Path

from rag_components.rag_manager import RAGManager
from core.config import DEFAULT_DOCS_DIR

# Initialize one RAGManager instance to be shared by the tools
rag_manager = RAGManager()

class IndexDirectoryInput(BaseModel):
    directory: str = Field(description="The path to the directory containing documents to index.", default=str(DEFAULT_DOCS_DIR))
    force_recreate: bool = Field(description="If true, deletes any existing index and creates a new one. Default is false.", default=False)

class IndexDirectoryTool(BaseTool):
    name: str = "index_document_directory"
    description: str = "Processes and indexes all .txt and .pdf documents from a specified directory into the knowledge base. Use this to add new course materials."
    args_schema: Type[BaseModel] = IndexDirectoryInput

    def _run(self, directory: str, force_recreate: bool) -> str:
        source_path = Path(directory)
        return rag_manager.build_or_update_index(source_path, force_recreate)

class QueryKnowledgeBaseInput(BaseModel):
    query: str = Field(description="The question to ask the knowledge base.")

class QueryKnowledgeBaseTool(BaseTool):
    name: str = "query_knowledge_base"
    description: str = "Queries the indexed knowledge base of your documents to answer a question."
    args_schema: Type[BaseModel] = QueryKnowledgeBaseInput

    def _run(self, query: str) -> str:
        qa_chain = rag_manager.get_qa_chain()
        if not qa_chain:
            return "Knowledge base not initialized. Please index a directory first using the 'index_document_directory' tool."
        
        result = qa_chain.invoke({"query": query})
        
        answer = result.get('result', 'Could not find an answer.')
        sources = result.get('source_documents', [])
        
        if sources:
            source_files = list(set([doc.metadata.get('source', 'N/A') for doc in sources]))
            answer += f"\n\nSources Used: {', '.join(source_files)}"
            
        return answer