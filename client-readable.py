# Client for MCP server with human-readable output formatting
# Connects to a local MCP server and uses AWS Bedrock to invoke Claude 3.5 Sonnet
import asyncio  # For async/await support
import json     # For JSON formatting in output
from mcp import ClientSession  # MCP client session management
from mcp.client.streamable_http import streamablehttp_client  # HTTP transport for MCP

from langgraph.prebuilt import create_react_agent  # Creates a ReAct agent (reasoning + action)
from langchain_mcp_adapters.tools import load_mcp_tools  # Loads tools from MCP server

# Helper function to format different message types for readable console output
def print_message(message):
    if hasattr(message, 'content'):
        if isinstance(message.content, str):
            # Simple text message from AI
            print(f"AI: {message.content}")
        elif isinstance(message.content, list):
            # Process structured content (text and tool calls)
            for item in message.content:
                if item.get('type') == 'text':
                    # Display AI's reasoning text
                    print(f"AI: {item['text']}")
                elif item.get('type') == 'tool_use':
                    # Display tool calls with formatted parameters
                    print(f"TOOL CALL: {item['name']}({json.dumps(item['input'], indent=2)})")
    elif hasattr(message, 'name') and hasattr(message, 'content'):
        # Display tool execution results
        print(f"TOOL RESULT ({message.name}): {message.content}")

async def main():
    # Connect to the MCP server using HTTP transport
    # Returns read/write functions and a close function (unused, hence _)
    async with streamablehttp_client("http://0.0.0.0:3000/mcp") as (read, write, _):
        # Create an MCP client session using the transport
        async with ClientSession(read, write) as session:
            # Initialize the connection to the MCP server
            await session.initialize()

            # Load available tools from the MCP server
            tools = await load_mcp_tools(session)
            
            # Create a ReAct agent using AWS Bedrock's Claude 3.5 Sonnet model
            # This agent will use the tools from the MCP server
            agent = create_react_agent("bedrock_converse:anthropic.claude-3-5-sonnet-20240620-v1:0", tools)
            
            # Define the query to send to the agent
            query = "what's (3 + 5) x 12? and what is 3789 + 2442? Why is the sky blue?"
            print(f"\nQUESTION: {query}\n")
            
            # Invoke the agent with the query
            # The agent will reason about the query and use tools as needed
            math_response = await agent.ainvoke({"messages": query})
            
            # Display the conversation in a readable format
            print("\n--- CONVERSATION ---")
            for message in math_response["messages"]:
                if message.type == "human":
                    # Display the human's message
                    print(f"\nHUMAN: {message.content}")
                else:
                    # Display AI responses and tool interactions
                    print("")
                    print_message(message)

# Standard Python idiom to run the main function when script is executed directly
if __name__ == "__main__":
    asyncio.run(main())  # Run the async main function in the event loop
