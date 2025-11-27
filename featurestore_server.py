# featurestore_server.py
import json

from mcp.server.fastmcp import FastMCP

from database import get_db_connection, init_db

# Initialize the MCP Server
mcp = FastMCP("FeatureStoreLite")

# Ensure DB is ready when server starts
init_db()


@mcp.resource("schema://main")
def get_schema() -> str:
    """
    Resource: Provide the database schema.
    Resources are passive data that LLMs can read like files.
    """
    conn = get_db_connection()
    try:
        schema = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table'"
        ).fetchall()
        return "\n".join(sql[0] for sql in schema if sql[0]) or "No tables found."
    finally:
        conn.close()


@mcp.tool()
def store_feature(key: str, vector: str, metadata: str | None = None) -> str:
    """
    Tool: Store a feature vector.
    Tools are executable functions that LLMs can call to perform actions.
    """
    conn = get_db_connection()
    try:
        # Validate that vector is valid JSON
        json.loads(vector)

        conn.execute(
            "INSERT OR REPLACE INTO features (key, vector, metadata) VALUES (?, ?, ?)",
            (key, vector, metadata),
        )
        conn.commit()
        return f"Successfully stored feature '{key}'"
    except json.JSONDecodeError:
        return "Error: Vector must be a valid JSON array string (e.g., '[0.1, 0.2]')"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
def get_feature(key: str) -> str:
    """
    Tool: Retrieve a feature vector by key.
    """
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT vector, metadata FROM features WHERE key = ?", (key,)
        ).fetchone()

        if row:
            return json.dumps(
                {
                    "key": key,
                    "vector": json.loads(row[0]),
                    "metadata": json.loads(row[1]) if row[1] else None,
                },
                indent=2,
            )
        return f"Feature '{key}' not found."
    finally:
        conn.close()


@mcp.tool()
def list_features() -> str:
    """
    Tool: List all available feature keys.
    """
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT key FROM features").fetchall()
        return json.dumps([row[0] for row in rows])
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run()
