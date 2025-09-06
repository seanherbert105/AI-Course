import os
import weaviate
from typing import Any, Dict, List
from fastmcp import FastMCP

# ====== CONFIG (env) ======
WEAVIATE_FIELDS = [
    f.strip() for f in os.getenv("WEAVIATE_FIELDS", "filename,content").split(",") if f.strip()
]

mcp = FastMCP()

@mcp.tool()
def weaviate_search(query_text: str) -> List[Dict[str, Any]]:
    """Query Weaviate for semantically similar objects.

    Args:
        query_text: Text to search for.
        limit: Max number of results to return.

    Returns: List of objects with selected fields.
    """
    # Connect to Weaviate
    client = weaviate.connect_to_custom(
        http_host="weaviate",
        http_port=8080,
        http_secure=False,
        grpc_host="weaviate",
        grpc_port=50051,
        grpc_secure=False,
    )

    """Search Weaviate for relevant chunks."""
    collection = client.collections.get("Eval")
    result = collection.query.near_text(
        query=query_text,
        return_properties=WEAVIATE_FIELDS,
    )

    # Extract results robustly
    docs: List[Dict[str, Any]] = []
    try:
        for o in result.objects:
            row = {k: o.properties.get(k) for k in WEAVIATE_FIELDS}
            docs.append(row)
    except Exception as exc:
        return [{"error": f"Query failed: {exc}"}]

    return docs

if __name__ == "__main__":
    mcp.run()