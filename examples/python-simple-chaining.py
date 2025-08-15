#!/usr/bin/env python3
"""
Simple API Chaining Example - Camino AI Python SDK

This example shows the basic pattern of chaining Camino AI APIs:
Context → Query → Journey

Perfect for understanding the workflow before building more complex applications.
"""

import asyncio
import os
from camino_ai import (
    CaminoAI,
    ContextRequest,
    QueryRequest, 
    JourneyRequest,
    Coordinate,
    Waypoint,
    JourneyConstraints,
    TransportMode,
)


async def simple_chaining_example():
    """Simple example of chaining context → query → journey APIs."""
    
    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ Please set CAMINO_API_KEY environment variable")
        return
    
    print("🔗 Simple API Chaining Example")
    print("=" * 35)
    
    async with CaminoAI(api_key=api_key) as client:
        
        # Starting location: Central Park, NYC
        start_location = Coordinate(lat=40.7831, lng=-73.9712)
        print(f"📍 Starting location: Central Park ({start_location.lat}, {start_location.lon})")
        
        # ============================================
        # STEP 1: Use /context to discover the area
        # ============================================
        print("\n1️⃣ Getting area context...")
        
        context_request = ContextRequest(
            location=start_location,
            radius="1000m",
            context="Find interesting places and attractions nearby"
        )
        
        try:
            context_response = await client.context_async(context_request)
            print(f"✅ Area context retrieved:")
            
            # Display context information
            if hasattr(context_response, 'context') and context_response.context:
                for key, value in list(context_response.context.items())[:3]:
                    print(f"   • {key}: {value}")
            
            # Check if we got nearby places from context
            nearby_count = len(context_response.nearby) if hasattr(context_response, 'nearby') and context_response.nearby else 0
            print(f"   • Found {nearby_count} nearby places in context")
            
        except Exception as e:
            print(f"❌ Context request failed: {e}")
            return
        
        # ============================================
        # STEP 2: Use /query to find specific POIs
        # ============================================
        print("\n2️⃣ Querying for specific POIs...")
        
        # Based on context, query for restaurants and cafes
        poi_queries = [
            "Italian restaurants near Central Park",
            "coffee shops with outdoor seating", 
            "museums and cultural attractions"
        ]
        
        all_pois = []
        
        for query_text in poi_queries:
            print(f"   🔍 Searching: {query_text}")
            
            query_request = QueryRequest(
                q=query_text,
                lat=start_location.lat,
                lon=start_location.lon,
                radius=1000,
                limit=2  # Get top 2 results per query
            )
            
            try:
                query_response = await client.query_async(query_request)
                
                print(f"      Found {len(query_response.results)} results:")
                for result in query_response.results:
                    print(f"      • {result.name}")
                    all_pois.append(result)
                    
            except Exception as e:
                print(f"      ❌ Query failed: {e}")
        
        print(f"\n   ✅ Total POIs collected: {len(all_pois)}")
        
        if not all_pois:
            print("❌ No POIs found, cannot plan journey")
            return
        
        # ============================================
        # STEP 3: Use /journey to plan optimal route
        # ============================================
        print("\n3️⃣ Planning optimal journey...")
        
        # Select top 3 POIs for our journey
        selected_pois = all_pois[:3]
        
        # Create waypoints: start + selected POIs
        waypoints = [
            # Start point
            Waypoint(
                location=start_location,
                purpose="start_point"
            )
        ]
        
        # Add POI waypoints
        for i, poi in enumerate(selected_pois):
            waypoints.append(
                Waypoint(
                    location=poi.coordinate,
                    purpose=f"visit_{poi.category or 'poi'}"
                )
            )
        
        journey_request = JourneyRequest(
            waypoints=waypoints,
            constraints=JourneyConstraints(
                transport="walking",
                time_budget="3h",
                preferences=["scenic"]
            )
        )
        
        try:
            journey_response = await client.journey_async(journey_request)
            
            print("✅ Journey planned successfully!")
            print(f"   📏 Total distance: {journey_response.total_distance/1000:.1f} km")
            print(f"   ⏱️  Total duration: {journey_response.total_duration/60:.0f} minutes")
            print(f"   🛤️  Route segments: {len(journey_response.segments)}")
            
            # Show the planned stops
            print(f"\n   🎯 Planned stops:")
            for i, poi in enumerate(selected_pois, 1):
                print(f"      {i}. {poi.name}")
                if poi.address:
                    print(f"         {poi.address}")
            
            # Show first few route instructions
            if journey_response.segments:
                print(f"\n   🧭 Route preview:")
                for i, segment in enumerate(journey_response.segments[:2], 1):
                    if hasattr(segment, 'instructions') and segment.instructions:
                        print(f"      {i}. {segment.instructions}")
                        print(f"         ({segment.distance:.0f}m, {segment.duration/60:.0f} min)")
            
        except Exception as e:
            print(f"❌ Journey planning failed: {e}")
            return
        
        # ============================================
        # STEP 4: Summary
        # ============================================
        print("\n🎉 API Chaining Complete!")
        print("=" * 25)
        print("✅ Context: Discovered area information")
        print(f"✅ Query: Found {len(all_pois)} POIs across {len(poi_queries)} searches")
        print(f"✅ Journey: Planned route through {len(selected_pois)} stops")
        print(f"📊 Total workflow distance: {journey_response.total_distance/1000:.1f} km")


async def main():
    """Run the simple chaining example."""
    await simple_chaining_example()


if __name__ == "__main__":
    asyncio.run(main())