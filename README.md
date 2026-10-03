# FeatureStoreLite MCP Server Example

A small MCP server, built with the FastMCP API of the official MCP Python SDK (v1), that stores and returns ML feature vectors from a local SQLite database. It is the companion code for the article [MCP Server Tutorial: Build with Python, uv, and FastMCP](https://slavadubrov.github.io/blog/2025/06/10/mcp-server-tutorial-uv-fastmcp/).

The server exposes:

- three tools: `get_feature`, `store_feature`, `list_features`
- one resource: `schema://main`, the database's `CREATE TABLE` statement

## Setup

Install [uv](https://docs.astral.sh/uv/), then:

```bash
git clone https://github.com/slavadubrov/mcp-featurestore
cd mcp-featurestore
uv sync --locked
uv run python database.py   # create features.db with two seed rows
```

The project pins `mcp[cli]>=1.28,<2`. The code uses the v1 API (`mcp.server.fastmcp`).

## Check the server

Call every tool through an in-memory MCP client:

```bash
uv run python test_server.py
```

Or open the MCP Inspector and call the tools by hand:

```bash
uv run mcp dev featurestore_server.py
```

## Connect to Claude Desktop

Add the server to `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`), with absolute paths:

```json
{
    "mcpServers": {
        "featurestore": {
            "command": "uv",
            "args": [
                "run",
                "--directory",
                "/ABSOLUTE/PATH/TO/mcp-featurestore",
                "--locked",
                "mcp",
                "run",
                "/ABSOLUTE/PATH/TO/mcp-featurestore/featurestore_server.py"
            ]
        }
    }
}
```

`--directory` makes uv use this project's `uv.lock`, and `--locked` fails instead of changing it. Restart Claude Desktop after editing the file.
