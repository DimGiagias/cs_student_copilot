from pathlib import Path
import requests
import re

from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from core.config import DOWNLOADS_PATH
    
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

class DownloadPaperInput(BaseModel):
    paper_id: str = Field(description="The Semantic Scholar Paper ID of the paper to download.")

def download_paper_pdf(paper_id: str) -> str:
    """
    Attempts to find an open access PDF for a paper and download it.
    """
    details_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    params = {"fields": "title,isOpenAccess,openAccessPdf"}
    response = requests.get(details_url, params=params)

    if not response.ok:
        return f"Error: Could not retrieve paper details to find download link. Status: {response.status_code}"

    data = response.json()
    if not data.get("isOpenAccess") or not data.get("openAccessPdf"):
        return "Sorry, this paper is not available for free download (not Open Access)."
    
    pdf_url = data["openAccessPdf"]["url"]
    title = data.get("title", f"Untitled_Paper_{paper_id}")
    
    # Sanitize the title to create a safe filename (remove illegal characters and trim length)
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", title)[:150].strip()
    filename = f"{safe_filename}.pdf"
    
    try:
        print(f"Downloading '{title}' as '{filename}' from: {pdf_url}")        
        pdf_response = requests.get(pdf_url, stream=True, timeout=30)
        pdf_response.raise_for_status()

        DOWNLOADS_PATH.mkdir(exist_ok=True)
        save_path = DOWNLOADS_PATH / filename

        with open(save_path, 'wb') as f:
            for chunk in pdf_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return f"Successfully downloaded '{filename}' to the '{DOWNLOADS_PATH}' directory."
    except Exception as e:
        return f"An error occurred during download: {e}"

download_paper_tool = StructuredTool(
    name="download_paper_pdf",
    func=download_paper_pdf,
    description="Downloads the PDF of an Open Access paper to a local directory using its Semantic Scholar ID.",
    args_schema=DownloadPaperInput
)