# Demo Local Streamable HTTP MCP with LangGraph and Bedrock LLM

Adapted from the Python SDK for MCP and the LangChain MCP Adapters. 

### Steps to run locally 

1. Start the MCP Server
    - Validate the MCP Server is running with MCP Inspector
2. Run the python client to test the MCP server


## MCP Server

> Adapted from the [LangGraph MCP Simple StreamableHttp Stateless Server Example](https://github.com/langchain-ai/langchain-mcp-adapters/tree/main/examples/servers/streamable-http-stateless)

A stateless MCP server example demonstrating the StreamableHttp transport without maintaining session state. This example is ideal for understanding how to deploy MCP servers in multi-node environments where requests can be routed to any instance. In the example in this repo, only a single MCP server node is being used. 

### Features

- Uses the StreamableHTTP transport in stateless mode (mcp_session_id=None)
- Each request creates a new ephemeral connection
- No session state maintained between requests
- Task lifecycle scoped to individual requests
- Suitable for deployment in multi-node environments

The server exposes 2 tools. 

- Add
- Multiply

### Usage

1. In the terminal, make sure you are in overall folder for the sample. Do not navigate to the folder with the server.py file in it. 

2. Start the server

    ```bash
    # Using default port 3000
    uv run mcp-simple-streamablehttp-stateless

    # [Optional] Using custom port
    uv run mcp-simple-streamablehttp-stateless --port 3000

    # [Optional] Custom logging level
    uv run mcp-simple-streamablehttp-stateless --log-level DEBUG

    # [Optional] Enable JSON responses instead of SSE streams
    uv run mcp-simple-streamablehttp-stateless --json-response
    ```

3. If it is running correctly, you should see that the server is now running at a local address like `http://0.0.0.0:3000`. The MCP server will be accessible on the `/mcp` path. 

Make sure to leave the terminal with the server running open to use it in the inspector and client. 

### MCP Inspector

> https://modelcontextprotocol.io/docs/tools/inspector 

1. Run the inspector

    ```bash
        # This will start the inspector on a different port than the server is running
        npx @modelcontextprotocol/inspector
    ```

2. For Transport Type, select `Streamable HTTP` 
3. For URL, add `http://0.0.0.0:3000/mcp` or whatever localhost + port combo you're using

## Client

A Streamable HTTP Client written in Python that serves as a base file to test the HTTP transport method. This is very barebones but showcases how to use the Python SDK [mcp.client.streamable_http](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/client/streamable_http.py). 

This local client invokes the [LangGraph agent](https://langchain-ai.github.io/langgraph/agents/models/#specifying-a-model-by-name) that uses the Amazon Bedrock model for `create_react_agent`. 

### Usage

You can either use the `client.py` or the `client-readable.py` file to test the MCP server. 

- **Option 1:** `client.py` = This is what you'll see in most examples, it has a print statement at the end to see the full response output from the invoke of the agent. 
- **Option 2:** `client-readable.py` = Exact same functionality as the client.py file except that it has some additional code added to make the overall output and calling of the agent readable in the terminal output. 

#### Prerequisites 

1. AWS CLI credentials must allow access to Amazon Bedrock model that is called in the client. 
    - Run `aws configure` in the CLI to verify you have the correct access set up or that you have a profile assumed that has the needed `~/.aws/credentials` set (MacOS).

2. Run the following command to test the server. 

    ```bash
        # Option 1
        python client.py

        # Option 2
        python client-readable.py
    ```

To test different responses from the agent, adjust the line in the file that has the `agent.ainvoke()` to have a different message.
