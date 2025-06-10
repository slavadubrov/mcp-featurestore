# featurestore_server.py

import json
from mcp.server.fastmcp import FastMCP
from database import get_db_connection, init_db

mcp = FastMCP("FeatureStoreLite")

# Initialize database
init_db()


@mcp.resource("schema://main")
def get_schema() -> str:
    """Provide the database schema as a resource"""
    conn = get_db_connection()
    try:
        schema = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table'"
        ).fetchall()
        if not schema:
            return "No tables found in database"
        return "\n".join(sql[0] for sql in schema if sql[0])
    except Exception as e:
        return f"Error getting schema: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
def store_feature(key: str, vector: str, metadata: str | None = None) -> str:
    """Store a feature vector with optional metadata"""
    conn = get_db_connection()
    try:
        # Validate vector format (JSON array)
        json.loads(vector)
        conn.execute(
            "INSERT OR REPLACE INTO features (key, vector, metadata) "
            "VALUES (?, ?, ?)",
            (key, vector, metadata)
        )
        conn.commit()
        return f"Feature '{key}' stored successfully"
    except json.JSONDecodeError:
        return "Error: vector must be valid JSON"
    except Exception as e:
        return f"Error storing feature: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
def get_feature(key: str) -> str:
    """Retrieve a feature vector by key"""
    conn = get_db_connection()
    try:
        result = conn.execute(
            "SELECT vector, metadata FROM features WHERE key = ?", (key,)
        ).fetchone()
        if result:
            return json.dumps({
                "key": key,
                "vector": json.loads(result[0]),
                "metadata": json.loads(result[1]) if result[1] else None
            })
        else:
            return f"Feature '{key}' not found"
    except Exception as e:
        return f"Error retrieving feature: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
def list_features() -> str:
    """List all available feature keys"""
    conn = get_db_connection()
    try:
        result = conn.execute(
            "SELECT key, created_at FROM features ORDER BY created_at DESC"
        ).fetchall()
        features = [{"key": row[0], "created_at": row[1]} for row in result]
        return json.dumps(features)
    except Exception as e:
        return f"Error listing features: {str(e)}"
    finally:
        conn.close()


@mcp.resource("features://{key}")
def feature_resource(key: str) -> str:
    """Expose feature data via URI"""
    return get_feature(key)


if __name__ == "__main__":
    mcp.run()