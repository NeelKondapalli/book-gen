# Document Processing and AI Query System

A system for ingesting various document formats (PDF, EPUB, DOCX, TXT, XML), storing them in a vector database (ChromaDB), and performing queries or generating responses using the stored knowledge.

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install Pipenv if you haven't already:
```bash
pip install pipenv
```

3. Install dependencies:
```bash
pipenv install
```

You will need to have Ollama installed to use this application The system uses the DeepSeek-R1 8B model through Ollama for text generation. This models rivals OpenAI's o1 models on a variety of benchmarks.

## LLM Setup

To setup Ollama:

1. Install Ollama from [ollama.com](https://ollama.com/)

2. Pull the DeepSeek-R1 8B model:
```bash
ollama run deepseek-r1:8b
```

## Usage

The system provides three main commands through its CLI interface:

### 1. Ingest Documents

Process and store documents from a directory into a ChromaDB collection:

```bash
pipenv run python main.py ingest --dir DIRECTORY_NAME --name COLLECTION_NAME
```

- `DIR`: Path to the directory containing documents
- `COLLECTION_NAME`: Name for the ChromaDB collection

Supported file formats:
- PDF (.pdf)
- EPUB (.epub)
- Microsoft Word (.docx)
- Text files (.txt)
- XML files (.xml)

### 2. Test Query

Search through the ingested documents with a specific query:

```bash
pipenv run python main.py test_query --name COLLECTION_NAME --query "QUERY"
```

- `COLLECTION_NAME`: Name of the existing collection to query
- `QUERY`: Your search query in natural language

### 3. Generate Response

Generate AI responses based on the knowledge in the collection:

```bash
pipenv run python main.py generate --name COLLECTION_NAME --prompt "PROMPT"
```

- `COLLECTION_NAME`: Name of the existing collection to use
- `PROMPT`: Your prompt for generating a response

## Example Usage

```bash
# Ingest documents from a directory
pipenv run python main.py ingest --dir ./documents --name my_docs

# Query the collection
pipenv run python main.py test_query --name my_docs --query "What are the main topics covered?"

# Generate a response
pipenv run python main.py generate --name my_docs --prompt "Explore the theme of social isolation in the documents"
```

## Notes

- The system automatically splits large documents into smaller chunks for better processing
- Each document chunk is stored with a unique ID in the format: `filename-chunk-N`
- XML files are processed to extract clean text, removing all markup
- The ChromaDB collection is persistent and stored locally

## Error Handling

- If a file cannot be processed, an error message will be displayed
- Unsupported file formats will be skipped with a warning
- If a collection name doesn't exist for queries/generation, an appropriate error will be shown
