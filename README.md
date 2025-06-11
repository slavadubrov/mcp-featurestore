# FeatureStoreLite MCP Server Example

This repository contains a lightweight example implementation of a Feature Store MCP (Model Context Protocol) server built with FastMCP and Python. It demonstrates how to create a custom MCP server that ML engineers can use to store and retrieve machine learning features through Claude Desktop.

## Purpose

This code serves as a practical companion to the blog article "Building a Custom FeatureStoreLite MCP Server Using uv" - a step-by-step guide showing how to build your own feature store MCP server from scratch, run it with **uv**, and integrate it seamlessly with Claude Desktop.

The implementation showcases:

- Setting up a FastMCP server with Python
- Creating feature store operations (store, retrieve, list features)
- Running the server through uv for easy dependency management
- Integrating with Claude Desktop for interactive ML workflows

Perfect for ML engineers looking to understand MCP server development and build their own specialized tools.

## Setup and Installation

First, install **uv**:

```bash
brew install uv
```

Then clone this repository and set up the virtual environment:

```bash
# Clone the repository
git clone https://github.com/slavadubrov/mcp-featurestore
cd mcp-featurestore

# Create virtual environment and install dependencies
uv sync
```

## Initialize Database

```bash
source .venv/bin/activate && python database.py
```

## Run MCP Server

```bash
source .venv/bin/activate && mcp dev featurestore_server.py
```

## Connecting to Claude Desktop

To use the FeatureStoreLite server with Claude Desktop, update your Claude configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "featurestore": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/path/to/your/featurestore_server.py"
      ]
    }
  }
}
```

## Reference

Original article can be found at: https://slavadubrov.github.io/blog/2025/06/10/building-a-custom-featurestorelite-mcp-server-using-uv/
