from __future__ import annotations

import os

import uvicorn


def serve() -> None:
    uvicorn.run(
        "anw_kalan_evidence_agent.asgi:application",
        host=os.getenv("MCP_HOST", "127.0.0.1"),
        port=int(os.getenv("MCP_PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    serve()
