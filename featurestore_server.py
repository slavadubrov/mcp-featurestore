# featurestore_server.py
import json
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from database import get_db_connection, init_db

# Initialize the MCP Server
mcp = FastMCP("FeatureStoreLite")

# Ensure DB is ready when server starts
init_db()

# A float that rejects NaN and infinities
FiniteFloat = Annotated[float, Field(allow_inf_nan=False)]


@mcp.resource("schema://main")
def get_schema() -> str:
    """The CREATE TABLE statements of the feature store database."""
    conn = get_db_connection()
    try:
        schema = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table'"
        ).fetchall()
        return "\n".join(sql[0] for sql in schema if sql[0]) or "No tables found."
    finally:
        conn.close()


@mcp.tool()
def store_feature(
    key: str,
    vector: Annotated[list[FiniteFloat], Field(min_length=1)],
    metadata: dict[str, Any] | None = None,
) -> str:
    """Store a feature vector under key. Overwrites an existing key.

    vector: non-empty list of finite numbers, e.g. [0.1, 0.2].
    metadata: optional JSON object, e.g. {"type": "user"}.
    """
    metadata_json = None if metadata is None else json.dumps(metadata, allow_nan=False)
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO features (key, vector, metadata) VALUES (?, ?, ?)",
            (key, json.dumps(vector), metadata_json),
        )
        conn.commit()
    finally:
        conn.close()
    return f"Stored feature '{key}'"


@mcp.tool()
def get_feature(key: str) -> str:
    """Return the vector and metadata stored under key, as JSON.

    Call list_features first if you do not know the key.
    """
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT vector, metadata FROM features WHERE key = ?", (key,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise ValueError(f"Feature '{key}' not found. Call list_features for valid keys.")
    return json.dumps(
        {
            "key": key,
            "vector": json.loads(row[0]),
            "metadata": json.loads(row[1]) if row[1] else None,
        },
        indent=2,
    )


@mcp.tool()
def list_features() -> str:
    """Return a JSON array of every stored feature key."""
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT key FROM features").fetchall()
        return json.dumps([row[0] for row in rows])
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run()
