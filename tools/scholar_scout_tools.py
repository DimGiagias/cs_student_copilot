import requests
import re

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
    
class SemanticScholarInput(BaseModel):
    query: str = Field(description="The topic, keywords, or title to search for.")
    limit: int = Field(description="The maximum number of papers to return.", default=5)

def search_semantic_scholar(query: str, limit: int = 5) -> str:
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,url"
    }
    
    print(f"Searching Semantic Scholar with query: '{query}' and limit: {limit}")
    response = requests.get(base_url, params=params)

    if not response.ok:
        return f"API Error: Received status code {response.status_code}. Please try rephrasing your query."

    data = response.json()
    papers = data.get("data", [])

    if not papers:
        return f"No papers found for the query: '{query}'"

    results = []
    for i, paper in enumerate(papers):
        title = paper.get("title", "No Title Provided")
        abstract = paper.get("abstract", "No Abstract Provided")
        authors = ", ".join(author.get("name", "N/A") for author in paper.get("authors", []))
        url = paper.get("url", "No URL Provided")
        
        results.append(
            f"Result {i+1}:\n"
            f"  Title: {title}\n"
            f"  Authors: {authors}\n"
            f"  URL: {url}\n"
            f"  Abstract: {abstract}"
        )

    return "\n\n---\n\n".join(results)

semantic_scholar_tool = StructuredTool(
    name="semantic_scholar_search",
    func=search_semantic_scholar,
    description="Searches the Semantic Scholar academic paper database for a given query and returns a specified number of results.",
    args_schema=SemanticScholarInput
)

class PaperDetailsInput(BaseModel):
    paper_id: str = Field(description="The Semantic Scholar Paper ID (e.g., '649def34f8be52c8b66281af98ae884c09a45b20').")

def get_paper_details(paper_id: str) -> str:
    """
    Fetches detailed information for a single paper from Semantic Scholar using its ID.
    """
    base_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    params = {
        "fields": "title,abstract,authors,url,year,tldr"
    }
    
    print(f"Fetching details for paper: {paper_id}")
    response = requests.get(base_url, params=params)

    if not response.ok:
        return f"API Error: Could not fetch details for paper ID {paper_id}. Status: {response.status_code}"

    paper = response.json()
    
    title = paper.get("title", "N/A")
    abstract = paper.get("abstract", "N/A")
    authors = ", ".join(author.get("name", "N/A") for author in paper.get("authors", []))
    url = paper.get("url", "N/A")
    year = paper.get("year", "N/A")
    tldr = paper.get("tldr", {}).get("text") if paper.get("tldr") else "No TLDR available."

    return (
        f"Title: {title}\n"
        f"Authors: {authors}\n"
        f"Year: {year}\n"
        f"URL: {url}\n\n"
        f"TLDR (Too Long; Didn't Read):\n{tldr}\n\n"
        f"Abstract:\n{abstract}"
    )

get_paper_details_tool = StructuredTool(
    name="get_paper_details_and_summary",
    func=get_paper_details,
    description="Fetches a detailed summary (including abstract and TLDR) of a single academic paper using its specific Semantic Scholar ID.",
    args_schema=PaperDetailsInput
)