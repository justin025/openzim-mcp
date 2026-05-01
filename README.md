<p align="center">
  <img src="https://raw.githubusercontent.com/cameronrye/openzim-mcp/main/website/assets/logo.svg" alt="OpenZIM MCP Logo" width="120" height="120">
</p>

<h1 align="center">OpenZIM MCP Server</h1>

<p align="center">
  <strong>Transform static ZIM archives into dynamic knowledge engines for AI models</strong>
</p>

---

**OpenZIM MCP** is a modern, secure, and high-performance MCP (Model Context Protocol) server that enables AI models to access and search [ZIM format](https://en.wikipedia.org/wiki/ZIM_(file_format)) knowledge bases offline.

## Features

- **11 Specialized Tools**: Search, browse, and extract content from ZIM archives with dedicated tools
- **Multi-Archive Search**: Search every ZIM file at once with `search_all` — no need to know which archive holds the answer
- **Find Entries by Title**: Resolve titles to entry paths instantly with `find_entry_by_title` — case-insensitive, optionally cross-file
- **Security First**: Comprehensive input validation and path traversal protection
- **High Performance**: Intelligent caching and optimized ZIM file operations
- **Smart Retrieval**: Automatic fallback from direct access to search-based retrieval for reliable entry access
- **Well Tested**: 80%+ test coverage with comprehensive test suite
- **Modern Architecture**: Modular design with dependency injection
- **Type Safe**: Full type annotations throughout the codebase
- **Configurable**: Flexible configuration with validation
- **Observable**: Structured logging and health monitoring

## What's new in v0.9.0

### Multi-archive search

`search_all` queries every ZIM file in your allowed directories at once and merges the results — no need to know which archive holds the answer.

### Find entries by title

`find_entry_by_title` resolves a title (or partial title) to one or more entry paths, with case-insensitive matching. Cheaper than full-text search when you already know the article name.

### MCP Resources

MCP **resources** let your client's resource browser and `@`-mention picker see ZIM files directly:

- `zim://files` — index of all available ZIM files
- `zim://{name}` — overview of one ZIM (metadata, namespaces, main page preview)

## Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install openzim-mcp
```

### Installation from Source

```bash
# Clone the repository
git clone https://github.com/cameronrye/openzim-mcp.git
cd openzim-mcp

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Prepare ZIM Files

Download ZIM files (e.g., Wikipedia, Wiktionary, etc.) from the [Kiwix Library](https://browse.library.kiwix.org/) and place them in a directory:

```bash
mkdir ~/zim-files
# Download ZIM files to ~/zim-files/
```

### Running the Server

Activate your virtual environment first:
```bash
source venv/bin/activate
```

Then run:

```bash
openzim-mcp /path/to/zim/files
python -m openzim_mcp /path/to/zim/files
```

**HTTP transport (SSE or streamable-http):**

```bash
openzim-mcp --transport streamable-http --host 0.0.0.0 --port 8000 /path/to/zim/files
openzim-mcp --transport sse --host 0.0.0.0 --port 8000 /path/to/zim/files
```

**Or use environment variables:**

```bash
export OPENZIM_MCP_TRANSPORT=sse
export OPENZIM_MCP_HOST=0.0.0.0
export OPENZIM_MCP_PORT=9000
openzim-mcp /path/to/zim/files
```

### MCP Configuration

**stdio transport (default):**

```json
{
  "openzim-mcp": {
    "command": "openzim-mcp",
    "args": ["/path/to/zim/files"]
  }
}
```

**SSE transport:**

```json
{
  "openzim-mcp-sse": {
    "command": "openzim-mcp",
    "args": ["--transport", "sse", "--host", "0.0.0.0", "--port", "9000", "/path/to/zim/files"]
  }
}
```

**Streamable HTTP transport:**

```json
{
  "openzim-mcp-http": {
    "command": "openzim-mcp",
    "args": ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "9000", "/path/to/zim/files"]
  }
}
```

Alternative configuration using Python module:

```json
{
  "openzim-mcp": {
    "command": "python",
    "args": [
      "-m",
      "openzim_mcp",
      "/path/to/zim/files"
    ]
  }
}
```

For development (from source):

```json
{
  "openzim-mcp": {
    "command": "python",
    "args": [
      "-m",
      "openzim_mcp",
      "/path/to/zim/files"
    ]
  }
}
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=openzim_mcp --cov-report=html

# Run specific test file
python -m pytest tests/test_security.py -v
```

---

## API Reference

### Available Tools

### search_zim_files - Search ZIM file names by keyword

**Required parameters:**

- `query` (string): Keyword to match against ZIM file names (case-insensitive)
- `limit` (integer, default: 10): Maximum results to return

**Use this instead of `list_zim_files`** when you know part of the file name. Searching "nginx" returns only nginx-related archives instead of listing all 200 ZIM files.

### list_zim_files - List all ZIM files (compact by default)

**Optional parameters:**

- `directory` (string): Filter to a specific directory path
- `include_details` (boolean, default: false): Include size and modification date

Use as a last resort — prefer `search_zim_files` when you know part of the file name. Default output is compact (name + path only); set `include_details` for full metadata.

### search_zim_file - Search within ZIM file content

**Required parameters:**

- `zim_file_path` (string): Path to the ZIM file
- `query` (string): Search query term

**Optional parameters:**

- `limit` (integer, default: 10): Maximum number of results to return
- `offset` (integer, default: 0): Starting offset for results (for pagination)

### get_zim_entry - Get detailed content of a specific entry in a ZIM file

**Required parameters:**

- `zim_file_path` (string): Path to the ZIM file
- `entry_path` (string): Entry path, e.g., 'A/Some_Article'

**Optional parameters:**

- `max_content_length` (integer, default: 100000, minimum: 1000): Maximum length of returned content

**Smart Retrieval Features:**

- **Automatic Fallback**: If direct path access fails, automatically searches for the entry and uses the exact path found
- **Path Mapping Cache**: Caches successful path mappings for improved performance on repeated access
- **Enhanced Error Guidance**: Provides clear guidance when entries cannot be found, suggesting alternative approaches
- **Transparent Operation**: Works seamlessly regardless of path encoding differences (spaces vs underscores, URL encoding, etc.)

### list_namespaces - List available namespaces and their entry counts

**Required parameters:**

- `zim_file_path` (string): Path to the ZIM file

**Returns:**
JSON string containing namespace information with entry counts, descriptions, and sample entries for each namespace (C, M, W, X, etc.).

### search_with_filters - Search within ZIM file content with optional namespace and content type filters

**Required parameters:**

- `zim_file_path` (string): Path to the ZIM file
- `query` (string): Search query term

**Optional parameters:**

- `namespace` (string): Optional namespace filter (C, M, W, X, etc.)
- `content_type` (string): Optional content type filter (text/html, text/plain, etc.)
- `limit` (integer, default: 10, range: 1-100): Maximum number of results to return
- `offset` (integer, default: 0): Starting offset for pagination

**Returns:**
Filtered search results with namespace and content type information.

### extract_article_links - Extract internal and external links from an article

**Required parameters:**

- `zim_file_path` (string): Path to the ZIM file
- `entry_path` (string): Entry path, e.g., 'C/Some_Article'

**Returns:**
JSON string containing categorized links (internal, external, media) with titles and metadata.

### get_entry_summary - Get a concise article summary

**Required parameters:**

- `zim_file_path` (string): Path to the ZIM file
- `entry_path` (string): Entry path, e.g., 'C/Some_Article'

**Optional parameters:**

- `max_words` (integer, default: 200, range: 10-1000): Maximum number of words in the summary

**Returns:**
JSON string containing a concise summary extracted from the article's opening paragraphs, with metadata including title, word count, and truncation status.

**Features:**

- Extracts opening paragraphs while removing infoboxes, navigation, and sidebars
- Provides quick article overview without loading full content
- Useful for LLMs to understand article context before deciding to read more

### get_table_of_contents - Extract hierarchical table of contents

**Required parameters:**

- `zim_file_path` (string): Path to the ZIM file
- `entry_path` (string): Entry path, e.g., 'C/Some_Article'

**Returns:**
JSON string containing a hierarchical tree structure of article headings (h1-h6), suitable for navigation and content overview.

**Features:**

- Hierarchical tree structure with nested children
- Includes heading levels, text, and anchor IDs
- Provides heading count and maximum depth statistics
- Enables LLMs to navigate directly to specific sections

---

## Examples

### Listing ZIM files

```json
{
  "name": "list_zim_files"
}
```

Response:

```plain
Found 1 ZIM files in 1 directories:

[
  {
    "name": "wikipedia_en_100_2025-08.zim",
    "path": "C:\\zim\\wikipedia_en_100_2025-08.zim",
    "directory": "C:\\zim",
    "size": "310.77 MB",
    "modified": "2025-09-11T10:20:50.148427"
  }
]
```

### Searching ZIM files

```json
{
  "name": "search_zim_file",
  "arguments": {
    "zim_file_path": "C:\\zim\\wikipedia_en_100_2025-08.zim",
    "query": "biology",
    "limit": 3
  }
}
```

### Getting ZIM entries

```json
{
  "name": "get_zim_entry",
  "arguments": {
    "zim_file_path": "C:\\zim\\wikipedia_en_100_2025-08.zim",
    "entry_path": "Protein"
  }
}
```


### Smart Retrieval in Action

**Example: Automatic path resolution**

```json
{
  "name": "get_zim_entry",
  "arguments": {
    "zim_file_path": "C:\\zim\\wikipedia_en_100_2025-08.zim",
    "entry_path": "A/Test Article"
  }
}
```


### Additional Search Examples

**Computer-related search:**

```json
{
  "name": "search_zim_file",
  "arguments": {
    "zim_file_path": "C:\\zim\\wikipedia_en_100_2025-08.zim",
    "query": "computer",
    "limit": 2
  }
}
```

**Getting detailed content:**

```json
{
  "name": "get_zim_entry",
  "arguments": {
    "zim_file_path": "C:\\zim\\wikipedia_en_100_2025-08.zim",
    "entry_path": "Evolution",
    "max_content_length": 1500
  }
}
```

### Advanced Knowledge Retrieval Examples

**Filtered search:**

```json
{
  "name": "search_with_filters",
  "arguments": {
    "zim_file_path": "C:\\zim\\wikipedia_en_100_2025-08.zim",
    "query": "evolution",
    "namespace": "C",
    "content_type": "text/html",
    "limit": 3
  }
}
```

**Getting article summary:**

```json
{
  "name": "get_entry_summary",
  "arguments": {
    "zim_file_path": "C:\\zim\\wikipedia_en_100_2025-08.zim",
    "entry_path": "C/Evolution",
    "max_words": 100
  }
}
```

Response:

```json
{
  "title": "Evolution",
  "path": "C/Evolution",
  "content_type": "text/html",
  "summary": "Evolution is the change in heritable characteristics of biological populations over successive generations. These characteristics are the expressions of genes, which are passed from parent to offspring during reproduction...",
  "word_count": 100,
  "is_truncated": true
}
```

**Getting table of contents:**

```json
{
  "name": "get_table_of_contents",
  "arguments": {
    "zim_file_path": "C:\\zim\\wikipedia_en_100_2025-08.zim",
    "entry_path": "C/Evolution"
  }
}
```

Response:

```json
{
  "title": "Evolution",
  "path": "C/Evolution",
  "content_type": "text/html",
  "toc": [
    {
      "level": 1,
      "text": "Evolution",
      "id": "evolution",
      "children": [
        {
          "level": 2,
          "text": "History of evolutionary thought",
          "id": "history",
          "children": []
        },
        {
          "level": 2,
          "text": "Mechanisms",
          "id": "mechanisms",
          "children": []
        }
      ]
    }
  ],
  "heading_count": 15,
  "max_depth": 4
}
```

---

## ZIM Entry Retrieval Best Practices

### Smart Retrieval System

OpenZIM MCP implements an intelligent entry retrieval system that automatically handles path encoding inconsistencies common in ZIM files:

**How It Works:**

1. **Direct Access First**: Attempts to retrieve the entry using the provided path exactly as given
2. **Automatic Fallback**: If direct access fails, automatically searches for the entry using various search terms
3. **Path Mapping Cache**: Caches successful path mappings to improve performance for repeated access
4. **Enhanced Error Guidance**: Provides clear guidance when entries cannot be found

**Benefits for LLM Users:**

- **Transparent Operation**: No need to understand ZIM path encoding complexities
- **Single Tool Call**: Eliminates the need for manual search-first methodology
- **Reliable Results**: Consistent success across different path formats (spaces vs underscores, URL encoding, etc.)
- **Performance Optimized**: Cached mappings improve repeated access speed

**Example Scenarios Handled Automatically:**

- `A/Test Article` → `A/Test_Article` (space to underscore conversion)
- `C/Café` → `C/Caf%C3%A9` (URL encoding differences)
- `A/Some-Page` → `A/Some_Page` (hyphen to underscore conversion)

### Usage Recommendations

**For Direct Entry Access:**

```json
{
  "name": "get_zim_entry",
  "arguments": {
    "zim_file_path": "/path/to/file.zim",
    "entry_path": "A/Article_Name"
  }
}
```

**When Entry Not Found:**
The system will automatically provide guidance:

```
Entry not found: 'A/Article_Name'.
The entry path may not exist in this ZIM file.
Try using search_zim_file() to find available entries,
or list_namespaces() to explore the file structure.
```

---

## Important Notes and Limitations

### Content Length Requirements

- The `max_content_length` parameter for `get_zim_entry` must be at least 1000 characters
- Content longer than the specified limit will be truncated with a note showing the total character count

### Search Behavior

- Search results may include articles that contain the search terms in various contexts
- Results are ranked by relevance but may not always be directly related to the primary meaning of the search term
- Search snippets provide a preview of the content but may not show the exact location where the search term appears

### File Format Support

- Currently supports ZIM files (Zeno IMproved format)
- Tested with Wikipedia ZIM files (e.g., `wikipedia_en_100_2025-08.zim`)
- File paths must be properly escaped in JSON (use `\\` for Windows paths)

---

## Configuration

OpenZIM MCP supports configuration through environment variables with the `OPENZIM_MCP_` prefix:

```bash
# Cache configuration
export OPENZIM_MCP_CACHE__ENABLED=true
export OPENZIM_MCP_CACHE__MAX_SIZE=200
export OPENZIM_MCP_CACHE__TTL_SECONDS=7200

# Content configuration
export OPENZIM_MCP_CONTENT__MAX_CONTENT_LENGTH=200000
export OPENZIM_MCP_CONTENT__SNIPPET_LENGTH=2000
export OPENZIM_MCP_CONTENT__DEFAULT_SEARCH_LIMIT=20

# Logging configuration
export OPENZIM_MCP_LOGGING__LEVEL=DEBUG
export OPENZIM_MCP_LOGGING__FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Server configuration
export OPENZIM_MCP_SERVER_NAME=my_openzim_mcp_server
```

### Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENZIM_MCP_CACHE__ENABLED` | `true` | Enable/disable caching |
| `OPENZIM_MCP_CACHE__MAX_SIZE` | `100` | Maximum cache entries |
| `OPENZIM_MCP_CACHE__TTL_SECONDS` | `3600` | Cache TTL in seconds |
| `OPENZIM_MCP_CONTENT__MAX_CONTENT_LENGTH` | `100000` | Max content length |
| `OPENZIM_MCP_CONTENT__SNIPPET_LENGTH` | `1000` | Max snippet length |
| `OPENZIM_MCP_CONTENT__DEFAULT_SEARCH_LIMIT` | `10` | Default search result limit |
| `OPENZIM_MCP_LOGGING__LEVEL` | `INFO` | Logging level |
| `OPENZIM_MCP_LOGGING__FORMAT` | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log message format |
| `OPENZIM_MCP_SERVER_NAME` | `openzim-mcp` | Server instance name |
| `OPENZIM_MCP_TRANSPORT` | `stdio` | Transport type (stdio, sse, streamable-http) |
| `OPENZIM_MCP_HOST` | `127.0.0.1` | Host to bind for HTTP transports |
| `OPENZIM_MCP_PORT` | `8000` | Port to bind for HTTP transports |

