# Aidien

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/198416177?v=4&size=200" alt="Project Logo" />
</p>

Aidien is an open-source project designed to process source code files by embedding them into a PostgreSQL database, performing vector similarity searches, and updating the code based on natural language queries using a large language model (LLM).

## Features

- Recursively scans directories for supported programming languages.
- Chunks files by word count and computes normalized embeddings.
- Stores embeddings in a PostgreSQL database (using the pgvector extension).
- Uses Tree-sitter for AST extraction.
- Processes natural language queries to update code via an LLM (e.g., OpenAI).

## Requirements

- Python 3.8+
- PostgreSQL 11+ with pgvector extension
- See [requirements.txt](requirements.txt) for Python dependencies

## Database Setup

1. **Install PostgreSQL:**
   - Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
   - Or use your package manager:
     ```bash
     # Ubuntu/Debian
     sudo apt-get install postgresql

     # macOS with Homebrew
     brew install postgresql
     ```

2. **Install pgvector extension:**
   - First, install the development packages:
     ```bash
     # Ubuntu/Debian
     sudo apt-get install postgresql-server-dev-all

     # macOS with Homebrew
     brew install libpq
     ```
   - Then install pgvector:
     ```bash
     # Clone and build pgvector
     git clone https://github.com/pgvector/pgvector.git
     cd pgvector
     make
     sudo make install
     ```

3. **Configure Database:**
   - Create a new database and enable the pgvector extension:
     ```sql
     CREATE DATABASE your_database_name;
     \c your_database_name
     CREATE EXTENSION vector;
     ```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Deep-Commit/Aidien.git
   cd Aidien
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install as a module:**
   ```bash
   pip install .
   ```

## Usage

### Command Line Interface (CLI)

You can use Aidien as a CLI tool to embed files and process queries over your codebase.

```bash
python -m aidien --env path/to/.env --directory path/to/code --query "Add doc strings to all the functions explaining what they do."
```

- `--env`: Path to the `.env` file containing configuration variables.
- `--directory`: Directory to scan for code files.
- `--query`: The natural language query to process.

### Using as a Module

You can also use Aidien as a module in your Python code:

```python
from aidien.core import Aidien

# Initialize Aidien
aidien = Aidien(
    env_path="path/to/.env",
    target_directory="path/to/code",
    database_url="your_database_url",
    embed_model_name="your_embed_model_name",
    openai_api_key="your_openai_api_key",
    openai_model="gpt-4o"
)

# Embed a directory
aidien.embed_directory()

# Process a query
aidien.process_query("Add doc strings to all the functions explaining what they do.")
```

## TODO

- [ ] Optimize embedding code
- [ ] Improve context sent to LLM
- [ ] Support for more LLMs
- [ ] Support for hosted embedding models
