from langchain.tools import Tool
import requests

def search_semantic_scholar(query: str) -> str:
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": 5,
        "fields": "title,abstract,authors,url"
    }
    response = requests.get(base_url, params=params)
    if not response.ok:
        return f"Error: {response.status_code} - {response.text}"

    data = response.json()
    results = []
    for paper in data.get("data", []):
        title = paper.get("title", "No title")
        abstract = paper.get("abstract", "No abstract")
        authors = ", ".join(author["name"] for author in paper.get("authors", []))
        url = paper.get("url", "")
        results.append(f" {title}\n {authors}\n {url}\n\n{abstract}\n")

    return "\n---\n".join(results)

semantic_scholar_tool = Tool(
    name="SemanticScholarSearch",
    func=search_semantic_scholar,
    description="Search academic papers using Semantic Scholar by providing a topic or keywords."
)