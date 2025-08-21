#!/usr/bin/env python3
"""
Camino AI MCP + LangChain Integration Example

This example demonstrates how to integrate Camino AI's location intelligence 
MCP server with LangChain to create a powerful location-aware AI agent.

Requirements:
- pip install langchain-mcp-adapters langgraph langchain-anthropic
- Camino AI API key from https://app.getcamino.ai
- Anthropic API key

Usage:
1. Set your API keys in environment variables
2. Run the script to start an interactive location intelligence agent
"""

import asyncio
import os
from typing import List, Dict, Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage
import json
from dotenv import load_dotenv

load_dotenv()

# Configuration
CAMINO_API_KEY = os.getenv("CAMINO_API_KEY", "your_camino_api_key_here")
ANTHROPIC_API_KEY = os.getenv(
    "ANTHROPIC_API_KEY", "your_anthropic_api_key_here")


class CaminoLocationAgent:
    """
    A location-intelligent AI agent powered by Camino AI's MCP server
    """

    def __init__(self, camino_api_key: str, anthropic_api_key: str):
        self.camino_api_key = camino_api_key
        self.anthropic_api_key = anthropic_api_key
        self.model = ChatAnthropic(
            model="claude-3-5-sonnet-latest",
            api_key=anthropic_api_key,
            temperature=0.1
        )
        self.agent = None
        self.client = None

    async def setup_mcp_client(self):
        """
        Set up the MultiServerMCPClient with Camino AI's MCP server
        """
        # Configure Camino AI MCP server using the remote HTTP transport
        mcp_config = {
            "camino-ai": {
                "url": f"https://mcp.getcamino.ai/mcp?caminoApiKey={self.camino_api_key}",
                "transport": "streamable_http",
                # Optional: Add headers if needed
                "headers": {
                    "User-Agent": "LangChain-MCP-Client/1.0"
                }
            }
        }

        # Create the MultiServerMCPClient
        self.client = MultiServerMCPClient(mcp_config)

        # Get all available tools from the MCP servers
        tools = await self.client.get_tools()

        print(
            f"Connected to Camino AI MCP server. Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        # Create the agent with location intelligence tools
        self.agent = create_react_agent(
            self.model,
            tools,
            debug=True  # Enable debug mode to see tool calls
        )

        return tools

    async def query_location(self, user_query: str) -> str:
        """
        Process a location-based query using the Camino AI MCP server
        """
        if not self.agent:
            raise RuntimeError(
                "Agent not initialized. Call setup_mcp_client() first.")

        # Enhanced system prompt for location intelligence
        enhanced_query = f"""
        You are a location intelligence assistant powered by Camino AI. 
        Use the available location tools to provide detailed, contextual information about places, businesses, and routes.
        
        When providing recommendations:
        - Include specific details about atmosphere, crowd levels, and unique features
        - Consider practical factors like accessibility, parking, and nearby amenities
        - Provide context about neighborhoods and local characteristics
        - Suggest alternatives based on different preferences or needs
        
        User query: {user_query}
        """

        response = await self.agent.ainvoke({
            "messages": [HumanMessage(content=enhanced_query)]
        })

        return response["messages"][-1].content

    async def batch_location_queries(self, queries: List[str]) -> Dict[str, str]:
        """
        Process multiple location queries in batch
        """
        results = {}
        for i, query in enumerate(queries):
            print(f"Processing query {i+1}/{len(queries)}: {query}")
            try:
                result = await self.query_location(query)
                results[query] = result
            except Exception as e:
                results[query] = f"Error processing query: {str(e)}"

        return results

    async def interactive_session(self):
        """
        Start an interactive session for location queries
        """
        print("\nCamino AI Location Intelligence Agent")
        print("Ask me about places, businesses, routes, and local recommendations!")
        print("Type 'quit' to exit.\n")

        while True:
            try:
                user_input = input("Your location query: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Thanks for using Camino AI Location Intelligence!")
                    break

                if not user_input:
                    continue

                print("Searching for location information...")
                response = await self.query_location(user_input)
                print(f"\nResponse:\n{response}\n")
                print("-" * 80)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

    async def close(self):
        """
        Clean up resources
        """
        if self.client:
            await self.client.close()

# Example usage functions


async def example_queries():
    """
    Demonstrate various location intelligence capabilities
    """
    agent = CaminoLocationAgent(CAMINO_API_KEY, ANTHROPIC_API_KEY)

    try:
        # Setup the MCP client and agent
        await agent.setup_mcp_client()

        # Example queries showcasing different capabilities
        example_queries_list = [
            "Find quiet coffee shops near the Golden Gate Bridge",
            "What restaurants are within walking distance of Times Square?",
            "Plan a route from Central Park to the Museum of Natural History",
            "Find family-friendly attractions in downtown Seattle",
            "Recommend coworking spaces in the Mission District, San Francisco",
            "What are the best rooftop bars with views in Manhattan?"
        ]

        print("Running example location queries...\n")

        for query in example_queries_list:
            print(f"Query: {query}")
            response = await agent.query_location(query)
            print(f"Response: {response}\n")
            print("-" * 80)

            # Add small delay between queries to be respectful to the API
            await asyncio.sleep(1)

    finally:
        await agent.close()


async def custom_location_workflow():
    """
    Example of a custom workflow using Camino AI for trip planning
    """
    agent = CaminoLocationAgent(CAMINO_API_KEY, ANTHROPIC_API_KEY)

    try:
        await agent.setup_mcp_client()

        # Multi-step trip planning workflow
        trip_queries = [
            "Find highly-rated breakfast spots in SoHo, New York",
            "What museums are within walking distance of SoHo?",
            "Recommend lunch places near the Metropolitan Museum of Art",
            "Find evening entertainment options in the Theater District",
            "Plan the most efficient route connecting these locations"
        ]

        print("Planning a day trip in NYC using Camino AI...\n")

        trip_plan = await agent.batch_location_queries(trip_queries)

        print("Complete Trip Plan:")
        for i, (query, response) in enumerate(trip_plan.items(), 1):
            print(f"\n{i}. {query}")
            print(f"   {response[:200]}..." if len(
                response) > 200 else f"   {response}")

    finally:
        await agent.close()

if __name__ == "__main__":
    # Check for required API keys
    if CAMINO_API_KEY == "your_camino_api_key_here":
        print("Please set your CAMINO_API_KEY environment variable")
        print("   Get your API key from: https://app.getcamino.ai")
        exit(1)

    if ANTHROPIC_API_KEY == "your_anthropic_api_key_here":
        print("Please set your anthropic_api_key environment variable")
        exit(1)

    print("Choose an option:")
    print("1. Run example queries")
    print("2. Custom trip planning workflow")
    print("3. Interactive session")

    choice = input("Enter your choice (1-3): ").strip()

    if choice == "1":
        asyncio.run(example_queries())
    elif choice == "2":
        asyncio.run(custom_location_workflow())
    elif choice == "3":
        agent = CaminoLocationAgent(CAMINO_API_KEY, ANTHROPIC_API_KEY)

        async def run_interactive():
            try:
                await agent.setup_mcp_client()
                await agent.interactive_session()
            finally:
                await agent.close()

        asyncio.run(run_interactive())
    else:
        print("Invalid choice. Please run the script again.")
