from __future__ import annotations

from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.routing import Mount

from .server import mcp_server


@asynccontextmanager
async def lifespan(app):
    async with mcp_server.session_manager.run():
        yield


application = Starlette(
    routes=[
        Mount(
            "/mcp",
            app=mcp_server.streamable_http_app(
                streamable_http_path="/",
                stateless_http=True,
                json_response=True,
            ),
        )
    ],
    lifespan=lifespan,
)
