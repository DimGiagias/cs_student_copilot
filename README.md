# CS Student Copilot 🤖

Developed for the "Intelligent Agents" course at the University of Piraeus, **CS Student Copilot** is an AI-powered assistant designed to help computer science students with coding, studying, and academic research. It provides a unified interface for code generation and debugging, knowledge base management, and academic paper search—all accessible via CLI or a user-friendly Streamlit web app.

## ✨Features

The CS Student Copilot is comprised of a coordinator that routes tasks to three specialized agents:

- **CodeHelper 👨‍💻**
  - Generate, debug, and explain code in Python or other languages.
  - Execute code snippets.
  - Analyze and improve code files or folders.
  - Read and summarize code files.

- **StudyBuddy 📖**
  - Creates a searchable knowledge base from your local `.pdf` and `.txt` files (e.g., lecture notes, e-books, documentation, articles).
  - Ask questions in natural language and get answers synthesized directly from your own documents, complete with source citations.
  - Uses a robust, custom chain to provide reliable and well-formatted answers without unpredictable agent behavior.

- **ScholarScout 🎓**
  - Uses the Semantic Scholar API to find relevant papers based on keywords, topics, or authors.
  - Retrieves detailed abstracts and "TL;DR" summaries for specific papers.
  - Can download the PDF of any open-access paper directly to a local folder, automatically naming the file with the paper's title.

## Quick Start

### Prerequisites
- Python 3.11 or higher.
- `git` for cloning the repository.
- **(For StudyBuddy):** A local Ollama instance running with an embedding model.

#### 1. Clone the Repository

```bash
git clone https://github.com/DimGiagias/cs_student_copilot.git
cd cs_student_copilot
```

#### 2. Setup Environment and Install Requirements

You can use the provided setup script for easy environment setup (on Linux):

with `uv`:

```bash
./setup.sh --uv
```

with `pip`:

```bash
./setup.sh
```
Or use the `requirements.txt` file directly:

```bash
pip install -r requirements.txt
```

#### 3. Configuration
The application requires an API key from [OpenRouter.ai](https://openrouter.ai/) to access free LLMs.

1. Create a .env file in the root of the project directory (an example is provided):
```bash
cp .env.example .env
```

2. Open the .env file and paste your OpenRouter API key:
```bash
OPENROUTER_API_KEY="your_openrouter_api_key_here"
```

> **Note:** For embedding, you need to set up a local Ollama model (see [Ollama documentation](https://ollama.com/)). We recommend `mxbai-embed-large`
```bash
ollama pull mxbai-embed-large
```

## Usage

### 🖥️Terminal (CLI)

Run the CLI tool:

```bash
python3 main_cli.py
```

#### Example Commands

- **CodeHelper:**
  ```bash
  python3 main_cli.py codehelper "Write a Python function to reverse a string."
  ```

- **StudyBuddy:**
  - Index documents:
    ```bash
    python3 main_cli.py studybuddy index --path ./my_notes
    ```
  - Ask a question:
    ```bash
    python3 main_cli.py studybuddy ask "Summarize the main concepts in my calculus notes."
    ```

- **ScholarScout:**
  ```bash
  python3 main_cli.py scholarscout "Find recent papers about transformers in NLP."
  ```

### 🌐Web Interface (Streamlit)

Launch the web app:

```bash
streamlit run app_streamlit.py
```

- Select your assistant from the sidebar.
- Chat with CodeHelper, StudyBuddy, or ScholarScout.
- Manage your knowledge base and view example prompts.


## 🛠️ Project Structure

- **agents/**  
  Contains the core logic for each agent (`code_helper.py`, `scholar_scout.py`, etc.) and the `coordinator.py` that routes user requests.

- **tools/**  
  Holds the specialized tools that agents use to interact with external services (like the Semantic Scholar API) or the local filesystem.

- **rag_components/**  
  Contains the `RAGManager`, which encapsulates all the logic for StudyBuddy's Retrieval-Augmented Generation capabilities.

- **core/**  
  Includes project-wide configuration (`config.py`) and centralized model loading services (`llm_service.py`).

- **main_cli.py**  
  The entry point for the command-line interface.

- **streamlit_app.py**  
  The entry point for the Streamlit web UI.

- **setup.sh**  
  A simple shell script to automate environment setup.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.



