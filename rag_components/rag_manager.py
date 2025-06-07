import shutil
from pathlib import Path
from typing import Optional

from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

from core.llm_service import get_llm, get_embedding_model
from core.config import CHROMA_PERSIST_DIR, RAG_LLM_MODEL, DEFAULT_LLM_MODEL

QA_TEMPLATE_STR = """
Use the following pieces of context to answer the question at the end.
Each piece of context is from a source file.
If you don't know the answer, just say that you don't know, DO NOT try to make up an answer.
When you use information from a source, you MUST cite the source file name (e.g., 'According to lecture_notes.pdf...').
Be thorough and check all provided context for relevant information.
---
Context:
{context}
---
Question: {question}
Helpful Answer:
"""

class RAGManager:
    """Manages the entire RAG pipeline, from document ingestion to querying."""
    def __init__(self, persist_directory: Path = CHROMA_PERSIST_DIR):
        self.persist_directory = persist_directory
        self.embedding_function = get_embedding_model()
        self.llm = get_llm(model_name=RAG_LLM_MODEL if RAG_LLM_MODEL else DEFAULT_LLM_MODEL)
        self.vector_store: Optional[Chroma] = self._load_vector_store()

    def _load_documents(self, data_path: Path) -> list:
        if not data_path.is_dir():
            return []
        
        # Document loaders.
        txt_loader = DirectoryLoader(str(data_path), glob="**/*.txt", loader_cls=TextLoader, show_progress=True, use_multithreading=True)
        pdf_loader = DirectoryLoader(str(data_path), glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True, use_multithreading=True)
        
        return txt_loader.load() + pdf_loader.load()

    def _split_documents(self, documents: list) -> list:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return text_splitter.split_documents(documents)

    def _load_vector_store(self) -> Optional[Chroma]:
        """Loads an existing Chroma vector store if it exists."""
        if self.persist_directory.exists():
            print(f"Loading existing vector store from: {self.persist_directory}")
            return Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embedding_function
            )
        return None

    def build_or_update_index(self, source_directory: Path, force_recreate: bool = False) -> str:
        """Builds a new index or updates an existing one from a source directory."""
        if not source_directory.exists():
            return f"Error: Source directory '{source_directory}' not found."

        if self.vector_store and force_recreate:
            print(f"Force recreating index. Deleting old index at {self.persist_directory}")
            shutil.rmtree(self.persist_directory)
            self.vector_store = None
        
        print(f"Loading documents from {source_directory}...")
        documents = self._load_documents(source_directory)
        if not documents:
            return "No new documents found to index."
        
        chunks = self._split_documents(documents)
        
        if self.vector_store is None:
            print("Creating new vector store.")
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedding_function,
                persist_directory=str(self.persist_directory)
            )
            return f"Successfully created new index with {len(chunks)} chunks from {len(documents)} documents."
        else:
            print(f"Adding {len(chunks)} new chunks to existing vector store.")
            self.vector_store.add_documents(chunks)
            return f"Successfully added {len(chunks)} new chunks from {len(documents)} documents to the index."

    def get_qa_chain(self) -> Optional[RetrievalQA]:
        """Builds and returns the RetrievalQA chain."""
        if not self.vector_store:
            print("Error: Vector store is not initialized. Please index documents first.")
            return None
        
        retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20}
        )
        
        prompt = PromptTemplate(template=QA_TEMPLATE_STR, input_variables=["context", "question"])
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        return qa_chain