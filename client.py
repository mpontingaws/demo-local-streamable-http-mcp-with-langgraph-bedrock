# Basic client code without the printing lines
# Print statement will print the entire output from the agent response

# Added to allow local run of client.py 
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools

async def main():
    async with streamablehttp_client("http://0.0.0.0:3000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create agent using the LangGraph pre-built ReAct agent 
            agent = create_react_agent("bedrock_converse:anthropic.claude-3-5-sonnet-20240620-v1:0", tools)

            # Invokes the agent
            # Can dynamically change the message for different responses
            math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12? and what is 3789 + 2442? Why is the sky blue?"})
            print(math_response)

if __name__ == "__main__":
    asyncio.run(main())
