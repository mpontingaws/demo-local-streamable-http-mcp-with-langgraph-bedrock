# Sample from -- https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/servers/simple-streamablehttp-stateless
# This file implements a stateless HTTP server that exposes mathematical tools (add, multiply)
# using the Model Context Protocol (MCP). It allows AI models to call these tools via HTTP.

import contextlib
import logging
from collections.abc import AsyncIterator

import anyio
import click

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import RedirectResponse, JSONResponse
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)

@click.command()
@click.option("--port", default=3000, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses instead of SSE streams",
)
def main(
    port: int,
    log_level: str,
    json_response: bool,
) -> int:
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create an MCP server instance
    app = Server("mcp-streamable-http-stateless-demo")

    # Define the tool implementation for handling tool calls
    # This function is called when a client invokes a tool
    @app.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        # Implement the "add" tool
        if name == "add":
            return [
                types.TextContent(
                    type="text",
                    text=str(arguments["a"] + arguments["b"])
                )
            ]
        # Implement the "multiply" tool
        elif name == "multiply":
            return [
                types.TextContent(
                    type="text",
                    text=str(arguments["a"] * arguments["b"])
                )
            ]
        # Handle unknown tool requests
        else:
            raise ValueError(f"Tool {name} not found")

    # Define the available tools and their schemas
    # This function is called when a client requests the list of available tools
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            # Define the "add" tool schema
            types.Tool(
                name="add",
                description="Adds two numbers",
                inputSchema={
                    "type": "object",
                    "required": ["a", "b"],
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "First number to add",
                        },
                        "b": {
                            "type": "number",
                            "description": "Second number to add",
                        },
                    },
                },
            ),
            # Define the "multiply" tool schema
            types.Tool(
                name="multiply",
                description="Multiplies two numbers",
                inputSchema={
                    "type": "object",
                    "required": ["a", "b"],
                    "properties": {
                        "a": {
                            "type": "number",
                            "description": "First number to multiply",
                        },
                        "b": {
                            "type": "number",
                            "description": "Second number to multiply",
                        },
                    },
                },
            )
        ]

    # Create the session manager with true stateless mode
    # This handles the HTTP communication for the MCP protocol
    # Stateful example: https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/servers/simple-streamablehttp
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,  # No event store needed for stateless mode
        json_response=json_response,  # Use JSON or SSE based on command-line option
        stateless=True,  # Enable stateless mode (no session persistence)
    )

    # Handler function for MCP requests
    # This function processes incoming HTTP requests for the /mcp endpoint
    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    # Define the application lifecycle manager
    # This ensures proper startup and shutdown of the session manager
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Define a handler for the root path to prevent 404 errors on the "/" path
    # Helps to debug if server is running correctly
    # Can be removed if never accessing the root path 
    async def homepage(request):
        return JSONResponse({
            "message": "MCP Streamable HTTP Stateless API",
            "endpoints": {
                "mcp": "/mcp"
            }
        })
        
    # Create an ASGI application using the transport
    # This sets up the web server with the defined routes and handlers
    starlette_app = Starlette(
        debug=True,  # Enable debug mode for development
        routes=[
            Route("/", homepage),  # Root path handler
            Mount("/mcp", app=handle_streamable_http),  # MCP endpoint
        ],
        lifespan=lifespan,  # Application lifecycle manager
    )

    ### The portion below is needed to run the starlette app for the mcp sever hosting locally ###

    # Import uvicorn here to avoid circular imports
    import uvicorn
    
    # Start the ASGI server using uvicorn
    # This runs the web server on the specified host and port
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

    # Return success code
    return 0
