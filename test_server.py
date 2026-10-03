"""Call the server's tools through an in-memory MCP client session.

Run with: uv run python test_server.py
"""

import anyio
from mcp.shared.memory import create_connected_server_and_client_session

from database import get_db_connection
from featurestore_server import mcp


async def main() -> None:
    async with create_connected_server_and_client_session(mcp._mcp_server) as client:
        tools = {tool.name for tool in (await client.list_tools()).tools}
        assert tools == {"get_feature", "store_feature", "list_features"}, tools

        schema = await client.read_resource("schema://main")
        assert "CREATE TABLE" in schema.contents[0].text

        found = await client.call_tool("get_feature", {"key": "user_123"})
        assert not found.isError and "premium" in found.content[0].text

        missing = await client.call_tool("get_feature", {"key": "nope"})
        assert missing.isError and "not found" in missing.content[0].text

        stored = await client.call_tool(
            "store_feature",
            {"key": "test_item", "vector": [0.5, 0.5], "metadata": {"type": "test"}},
        )
        assert not stored.isError, stored.content[0].text

        # FastMCP parses a JSON string argument, and Python's parser accepts NaN.
        for bad_vector in ([], ["a"], "[1, NaN]"):
            bad = await client.call_tool(
                "store_feature", {"key": "test_bad", "vector": bad_vector}
            )
            assert bad.isError, bad_vector

    conn = get_db_connection()
    conn.execute("DELETE FROM features WHERE key LIKE 'test_%'")
    conn.commit()
    conn.close()
    print("All checks passed.")


if __name__ == "__main__":
    anyio.run(main)
