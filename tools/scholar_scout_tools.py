from langchain.tools import StructuredTool
import requests
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