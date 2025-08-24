from __future__ import annotations

import json
import os
import sys
import weaviate
from typing import Any, Dict, List

import requests
from mcp.server.fastmcp import FastMCP, Context

# ====== CONFIG (env) ======
WEAVIATE_FIELDS = [
    f.strip() for f in os.getenv("WEAVIATE_FIELDS", "filename,content").split(",") if f.strip()
]

BACKEND_GENERATE_PATH = os.getenv("BACKEND_GENERATE_PATH", "/generate-pdf")
BACKEND_QUERY_PARAM = os.getenv("BACKEND_QUERY_PARAM", "query")
BACKEND_METHOD = os.getenv("BACKEND_METHOD", "GET").upper()
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
# ==========================

mcp = FastMCP("WeaviateMCP")

@mcp.tool(title="Weaviate semantic search", description="Search Weaviate with nearText and return matching objects.")
def weaviate_search(query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
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
        limit=limit,
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

@mcp.tool(title="Generate evaluation report", description="Call the backend to generate a new evaluation report (e.g., PDF) using the provided query/instructions.")
def generate_evaluation_report(query: str) -> Dict[str, Any]:
    """Call your existing backend report endpoint.

    By default, performs a GET to {BACKEND_URL}{BACKEND_GENERATE_PATH}?{BACKEND_QUERY_PARAM}=... .
    Configure method/path/query-param via env vars.
    """
    base = "http://app:8000".rstrip("/")
    path = BACKEND_GENERATE_PATH if BACKEND_GENERATE_PATH.startswith("/") else f"/{BACKEND_GENERATE_PATH}"
    url = f"{base}{path}"

    try:
        if BACKEND_METHOD == "GET":
            resp = requests.get(url, params={BACKEND_QUERY_PARAM: query}, timeout=REQUEST_TIMEOUT)
        elif BACKEND_METHOD == "POST":
            # Send as JSON body with the chosen param name
            resp = requests.post(url, json={BACKEND_QUERY_PARAM: query}, timeout=REQUEST_TIMEOUT)
        else:
            raise ValueError(f"Unsupported BACKEND_METHOD: {BACKEND_METHOD}")

        resp.raise_for_status()
        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw": resp.text}

        # Normalize a common shape for agents
        return {
            "ok": True,
            "endpoint": url,
            "method": BACKEND_METHOD,
            "request_param": BACKEND_QUERY_PARAM,
            "response": data,
        }
    except requests.HTTPError as he:
        return {"ok": False, "error": f"HTTP {he.response.status_code}: {he.response.text}", "endpoint": url}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "endpoint": url}


def main() -> None:
    # Start the MCP server using stdio transport by default
    mcp.run()


if __name__ == "__main__":
    # Allow `python weaviate_mcp_server.py` direct execution
    main()