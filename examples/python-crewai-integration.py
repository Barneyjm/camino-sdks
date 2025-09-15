#!/usr/bin/env python3

"""
CrewAI integration example for the Camino AI Python SDK.

This demonstrates how to integrate Camino AI's geospatial capabilities 
with CrewAI agents using the native Model Context Protocol (MCP) adapter
connecting to Camino AI's hosted MCP server.

Install dependencies:
    pip install 'crewai-tools[mcp]'

Run with: python examples/python-crewai-integration.py
"""

import os
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew
from crewai_tools.adapters.mcp_server_adapter import MCPServerAdapter, SseServerParams




def create_location_crew_with_mcp(camino_api_key: str) -> tuple[Agent, Agent, Agent]:
    """Create CrewAI crew with native MCP integration to Camino AI's hosted server."""
    
    # Configure connection to Camino AI's hosted MCP server
    server_params = SseServerParams(
        url=f"https://mcp.getcamino.ai/mcp?caminoApiKey={camino_api_key}",
        headers={
            "User-Agent": "CrewAI-MCP-Client/1.0"
        }
    )
    
    # Create agents with MCP tools from hosted server
    with MCPServerAdapter(server_params) as mcp_tools:
        
        # Location Intelligence Analyst
        location_analyst = Agent(
            role="Location Intelligence Analyst",
            goal="Analyze locations, find optimal spots, and provide geospatial insights using real-time data",
            backstory="""You are an expert location analyst with access to Camino AI's 
            advanced geospatial tools via MCP. You can query locations globally, 
            analyze spatial relationships, and provide contextual information about places.
            
            Available tools through MCP:
            - query_locations: Search for places using natural language
            - get_location_context: Get detailed area information
            - calculate_distance: Compute distances between points
            - plan_route: Plan optimal routes between locations
            
            Always use these tools to provide accurate, real-time location data.""",
            tools=mcp_tools,
            verbose=True
        )
        
        # Route Planning Specialist  
        route_planner = Agent(
            role="Route Planning Specialist", 
            goal="Plan optimal routes and analyze travel logistics using geospatial data",
            backstory="""You are a route planning expert with access to Camino AI's 
            routing capabilities through MCP integration. You specialize in creating 
            efficient travel plans using real-time geospatial data.
            
            Your MCP-powered expertise includes:
            - Planning routes for different transport modes
            - Calculating precise travel times and distances
            - Optimizing multi-stop journeys
            - Analyzing spatial relationships between locations
            
            Always use the MCP tools for accurate routing information.""",
            tools=mcp_tools,
            verbose=True
        )
        
        # Travel Advisor
        travel_advisor = Agent(
            role="Travel Experience Advisor",
            goal="Synthesize location and routing data to create comprehensive travel recommendations",
            backstory="""You are a travel advisor with access to comprehensive location 
            intelligence through Camino AI's MCP server. You combine location data 
            with routing information to create exceptional travel experiences.
            
            You excel at using MCP tools to:
            - Research destinations and local context
            - Plan efficient routes and itineraries
            - Find optimal meeting points for groups
            - Provide practical travel recommendations
            
            Use the available MCP tools to enhance your recommendations with real data.""",
            tools=mcp_tools,
            verbose=True
        )
        
        return location_analyst, route_planner, travel_advisor


def demonstrate_crewai_mcp_integration():
    """Demonstrate CrewAI integration with Camino AI using native MCP adapter."""
    
    print("🤖 CrewAI + Camino AI MCP Integration Demo")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('CAMINO_API_KEY')
    if not api_key:
        print("❌ Please set CAMINO_API_KEY environment variable")
        return
    
    try:
        # Create agents with native MCP integration
        location_analyst, route_planner, travel_advisor = create_location_crew_with_mcp(api_key)
    
        # Example 1: Restaurant Discovery and Analysis
        print("\n1️⃣ Restaurant Discovery Task")
        
        restaurant_task = Task(
            description="""Find the best Italian restaurants in Manhattan using location queries. 
            For each restaurant, get context about the surrounding area including nearby 
            attractions and accessibility. Use the MCP tools to:
            1. Query for Italian restaurants in Manhattan
            2. Get location context for top restaurants
            3. Provide detailed analysis and recommendations""",
            expected_output="""A comprehensive report of top Italian restaurants in Manhattan 
            with location context, nearby attractions, and detailed recommendations.""",
            agent=location_analyst
        )
        
        # Example 2: Group Meeting Point Optimization
        print("\n2️⃣ Group Meeting Point Task")
        
        meeting_task = Task(
            description="""Three friends are located at: Times Square (40.7589,-73.9851), 
            Central Park (40.7831,-73.9712), and Wall Street (40.7074,-74.0113). 
            Use the MCP tools to:
            1. Calculate distances between all locations
            2. Find the geographic center point
            3. Get context for the center area to find good meeting spots
            4. Suggest restaurants or cafes near the optimal meeting point""",
            expected_output="""Optimal meeting location with coordinates, nearby venue 
            recommendations, and travel distances for each person.""",
            agent=route_planner
        )
        
        # Example 3: Food Tour Planning
        print("\n3️⃣ Food Tour Planning Task")
        
        event_task = Task(
            description="""Plan a comprehensive food tour in Greenwich Village using MCP tools:
            1. Query for highly-rated restaurants of different cuisines in Greenwich Village
            2. Get location context for each restaurant
            3. Plan optimal walking routes between restaurants
            4. Calculate total walking time and distances
            5. Create a complete itinerary with timing recommendations""",
            expected_output="""Complete food tour itinerary with restaurant details, 
            optimized walking routes, time estimates, and practical recommendations.""",
            agent=travel_advisor
        )
    
        # Create and run crew with MCP-enabled agents
        crew = Crew(
            agents=[location_analyst, route_planner, travel_advisor],
            tasks=[restaurant_task, meeting_task, event_task],
            verbose=True,
            process="sequential"  # Execute tasks in sequence
        )
        
        print("\n🚀 Starting CrewAI MCP crew execution...")
        results = crew.kickoff()
        
        print("\n✅ CrewAI MCP Integration Results:")
        print("=" * 40)
        
        for i, result in enumerate(results.tasks_output, 1):
            print(f"\nTask {i} Results:")
            print("-" * 20)
            print(result.raw)
            
    except Exception as e:
        print(f"❌ CrewAI MCP integration failed: {e}")


def demonstrate_mcp_integration_patterns():
    """Show different MCP integration patterns for CrewAI."""
    
    print("\n🔧 MCP Integration Patterns")
    print("=" * 30)
    
    patterns = {
        "Hosted MCP Server Integration": """
# Connect to Camino AI's hosted MCP server

from crewai_tools.adapters.mcp_server_adapter import MCPServerAdapter, SseServerParams

# Configure connection to hosted Camino AI MCP server  
server_params = SseServerParams(
    url=f"https://mcp.getcamino.ai/mcp?caminoApiKey={your_api_key}",
    headers={"User-Agent": "CrewAI-MCP-Client/1.0"}
)

# Use within CrewAI agents - tools are auto-discovered
with MCPServerAdapter(server_params) as mcp_tools:
    geo_agent = Agent(
        role="Geospatial Analyst", 
        goal="Analyze locations and spatial data",
        tools=mcp_tools,  # Auto-discovered from hosted MCP server
        backstory="Expert in geospatial analysis using Camino AI"
    )
        """,
        
        "Multi-Agent MCP Workflow": """
# Multiple specialized agents with shared MCP tools from hosted server

# Connect to hosted Camino MCP server
server_params = SseServerParams(
    url=f"https://mcp.getcamino.ai/mcp?caminoApiKey={api_key}"
)

with MCPServerAdapter(server_params) as mcp_tools:
    location_researcher = Agent(
        role="Location Researcher",
        tools=mcp_tools,
        goal="Find and analyze locations"
    )
    
    route_planner = Agent(
        role="Route Planner", 
        tools=mcp_tools,
        goal="Plan optimal routes and calculate distances"
    )
    
    travel_advisor = Agent(
        role="Travel Advisor",
        tools=mcp_tools,
        goal="Create comprehensive travel recommendations"
    )
    
    crew = Crew(
        agents=[location_researcher, route_planner, travel_advisor],
        process="hierarchical"  # Or "sequential"
    )
        """,
        
        "Error Handling and Timeouts": """
# Robust MCP integration with error handling

try:
    server_params = StdioServerParams(
        command="python",
        args=["camino_mcp_server.py"],
        timeout=30,  # 30 second timeout
        env={"CAMINO_API_KEY": api_key}
    )
    
    with MCPServerAdapter(server_params) as mcp_tools:
        if not mcp_tools:
            raise Exception("No MCP tools available")
            
        agent = Agent(
            role="Location Agent",
            tools=mcp_tools,
            max_execution_time=60  # Agent timeout
        )
        
except Exception as e:
    print(f"MCP integration failed: {e}")
    # Fallback to direct API calls
        """
    }
    
    for title, pattern in patterns.items():
        print(f"\n{title}:")
        print(pattern)


def demonstrate_configuration_examples():
    """Show different configuration examples for CrewAI + Camino MCP integration."""
    
    print("\n⚙️ Configuration Examples")
    print("=" * 30)
    
    examples = {
        "Installation & Setup": """
# Install dependencies
pip install 'crewai-tools[mcp]'

# Environment setup
export CAMINO_API_KEY="your-api-key"

# Basic usage - connects to hosted Camino MCP server
from crewai import Agent, Crew
from crewai_tools.adapters.mcp_server_adapter import MCPServerAdapter, SseServerParams
        """,
        
        "Production MCP Configuration": """
# Production-ready hosted MCP server configuration
server_params = SseServerParams(
    url=f"https://mcp.getcamino.ai/mcp?caminoApiKey={os.getenv('CAMINO_API_KEY')}",
    timeout=30,  # Connection timeout
    headers={
        "User-Agent": "CrewAI-Production/1.0",
        "Accept": "application/json"
    }
)

# Tool filtering for specific use cases  
with MCPServerAdapter(server_params, 
                     tool_filter=["query_locations", "plan_route"]) as tools:
    agent = Agent(tools=tools, ...)
        """,
        
        "Advanced Error Handling": """
# Comprehensive error handling and fallbacks
def create_location_crew_safe(api_key: str):
    try:
        return create_location_crew_with_mcp(api_key)
    except Exception as mcp_error:
        print(f"MCP integration failed: {mcp_error}")
        print("Falling back to direct API integration...")
        
        # Fallback to direct Camino AI client
        from camino_ai import CaminoAI
        client = CaminoAI(api_key=api_key)
        
        # Create agents with direct API calls instead of MCP
        return create_fallback_agents(client)
        """,
        
        "Custom MCP Server Deployment": """
# Deploy Camino MCP server as a separate service
# camino_mcp_server.py (standalone)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    
    server = CaminoMCPServer(args.api_key)
    server.run(port=args.port)
    
# Then use SSE adapter instead of Stdio
from crewai_tools.adapters.mcp_server_adapter import SseServerParams

server_params = SseServerParams(
    url="http://localhost:8080/mcp"
)
        """
    }
    
    for title, example in examples.items():
        print(f"\n{title}:")
        print(example)


def main():
    """Main demonstration function."""
    
    print("🌍 Camino AI + CrewAI MCP Integration Examples")
    print("=" * 50)
    
    # Check API key
    if not os.getenv('CAMINO_API_KEY'):
        print("⚠️  No CAMINO_API_KEY found.")
        print("   Set CAMINO_API_KEY to run full MCP integration examples.\n")
    
    # Run demonstrations
    demonstrate_mcp_integration_patterns()
    
    if os.getenv('CAMINO_API_KEY'):
        demonstrate_crewai_mcp_integration()
    else:
        print("\n🔒 Full CrewAI MCP integration requires API key")
    
    demonstrate_configuration_examples()
    
    print("\n📚 Additional Resources:")
    print("   • CrewAI MCP Docs: https://docs.crewai.com/en/mcp/overview")
    print("   • Camino AI Docs: https://docs.getcamino.ai")
    print("   • MCP Protocol: https://modelcontextprotocol.io")
    print("   • MCPServerAdapter: https://docs.crewai.com/tools/mcp_server_adapter")
    
    print("\n✅ CrewAI MCP integration examples completed!")


if __name__ == "__main__":
    main()