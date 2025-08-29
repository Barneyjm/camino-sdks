#!/usr/bin/env python3
"""
Basic usage examples for the Camino AI Python SDK.

This script demonstrates the core functionality of the SDK including
queries, relationships, context, journeys, and routes.
"""

import asyncio
import os

from camino_ai import (
    CaminoAI,
    QueryRequest,
    RelationshipRequest,
    ContextRequest,
    JourneyRequest,
    RouteRequest,
    Coordinate,
    Waypoint,
    TransportMode,
    APIError,
)
from pydantic import ValidationError


async def main():
    """Run examples demonstrating Camino AI SDK functionality."""

    # Initialize client with API key from environment
    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ Please set CAMINO_API_KEY environment variable")
        return

    client = CaminoAI(api_key=api_key, base_url="http://localhost:8080")

    print("🌍 Camino AI Python SDK Examples")
    print("=" * 40)

    # Example 1: Basic Query
    print("\n1️⃣ Basic Search Example")
    try:
        response = await client.search_async("eiffel tower")
        print(f"✅ Found {len(response.results)} results")
        for i, result in enumerate(response.results[:3]):  # Show first 3
            print(f"   {i+1}. {result.display_name} - {result.lat}, {result.lon}")
    except APIError as e:
        print(f"❌ Query failed: {e.message}")

    try:
        response = await client.query_async("coffee shops in Manhattan")
        print(f"✅ Found {response.total} coffee shops")
        for i, result in enumerate(response.results[:3]):  # Show first 3
            print(f"   {i+1}. {result.name} - {result.address}")
    except APIError as e:
        print(f"❌ Query failed: {e.message}")

    # Example 2: Advanced Query with Parameters
    print("\n2️⃣ Advanced Query Example")
    try:
        central_park = Coordinate(lat=40.7831, lon=-73.9712)
        query_request = QueryRequest(
            query="Italian restaurants",
            lat=central_park.lat,
            lon=central_park.lon,
            radius=1000,  # 1km radius
            limit=5
        )
        response = await client.query_async(query_request)
        print(
            f"✅ Found {len(response.results)} Italian restaurants near Central Park")
        for result in response.results:
            confidence_str = f" (confidence: {result.confidence:.2f})" if result.confidence else ""
            print(f"   • {result.name}{confidence_str}")
    except APIError as e:
        print(f"❌ Advanced query failed: {e.message}")

    # Example 3: Spatial Relationship
    print("\n3️⃣ Spatial Relationship Example")
    try:
        central_park = Coordinate(lat=40.7831, lon=-73.9712)
        times_square = Coordinate(lat=40.7589, lon=-73.9851)

        relationship_request = RelationshipRequest(
            start=central_park,
            end=times_square,
            include=["distance", "direction", "travel_time", "description"]
        )
        response = await client.relationship_async(relationship_request)

        print(f"✅ Central Park to Times Square:")
        print(
            f"   Distance: {response.distance} ({response.actual_distance_km:.2f} km)")
        print(f"   Direction: {response.direction}")
        print(f"   Walking time: {response.walking_time}")
        print(f"   Driving time: {response.driving_time}")
        print(f"   Description: {response.description}")
    except APIError as e:
        print(f"❌ Relationship calculation failed: {e.message}")

    # Example 4: Location Context
    print("\n4️⃣ Location Context Example")
    try:
        context_request = ContextRequest(
            location=Coordinate(lat=40.7831, lon=-73.9712),  # Central Park
            radius=500,
            categories=["restaurant", "entertainment", "shopping"]
        )
        response = await client.context_async(context_request)

        print("✅ Context for Central Park area:")
        print(f"   Area description: {response.area_description}")
        print(f"   Search radius: {response.search_radius}")
        print(f"   Total places found: {response.total_places_found}")
        print("   Relevant places:")
        print(
            f"     Restaurants: {', '.join(response.relevant_places.restaurants)}")
        print(f"     Services: {', '.join(response.relevant_places.services)}")
        print(f"     Shops: {', '.join(response.relevant_places.shops)}")
        print(
            f"     Attractions: {', '.join(response.relevant_places.attractions)}")
    except APIError as e:
        print(f"❌ Context request failed: {e.message}")

    # Example 5: Multi-waypoint Journey
    print("\n5️⃣ Journey Planning Example")
    try:
        waypoints = [
            Waypoint(lat=40.7831, lon=-73.9712, purpose="Central Park"),
            Waypoint(lat=40.7589, lon=-73.9851, purpose="Times Square"),
            Waypoint(lat=40.7505, lon=-73.9934,
                     purpose="Empire State Building")
        ]

        journey_request = JourneyRequest(
            waypoints=waypoints,
            constraints={
                "transport": "walking",
                "time_budget": "2 hours"
            }
        )

        response = await client.journey_async(journey_request)

        print("✅ Walking journey:")
        print(f"   Feasible: {response.feasible}")
        print(f"   Total distance: {response.total_distance_km} km")
        print(f"   Total time: {response.total_time_formatted}")
        print(f"   Transport mode: {response.transport_mode}")
        print(f"   Route segments: {len(response.route_segments)}")

        for i, segment in enumerate(response.route_segments):
            print(
                f"   Segment {i+1}: {segment.from_.purpose} → {segment.to.purpose}")
            print(
                f"     Distance: {segment.distance_km} km, Time: {segment.estimated_time}")

        print(f"   Analysis: {response.analysis.summary}")
    except APIError as e:
        print(f"❌ Journey planning failed: {e.message}")

    # Example 6: Point-to-Point Route
    print("\n6️⃣ Point-to-Point Route Example")
    try:
        route_request = RouteRequest(
            start_lat=40.7831,
            start_lon=-73.9712,
            end_lat=40.7589,
            end_lon=-73.9851,
            mode="foot",
            include_geometry=True
        )

        response = await client.route_async(route_request)

        print("✅ Walking route:")
        print(
            f"   Distance: {response.summary.total_distance_meters:.1f} meters")
        print(
            f"   Duration: {response.summary.total_duration_seconds/60:.1f} minutes")
        print(f"   Instructions: {len(response.instructions)} steps")
        print(f"   Geometry included: {response.include_geometry}")

        # Show first few instructions
        if response.instructions:
            print("   First few instructions:")
            for i, instruction in enumerate(response.instructions[:3]):
                print(f"     {i+1}. {instruction}")
    except APIError as e:
        print(f"❌ Route calculation failed: {e.message}")

    # Close client
    await client.aclose()
    print("\n✨ Examples completed!")


def sync_examples():
    """Synchronous examples for comparison."""
    print("\n🔄 Synchronous API Examples")
    print("=" * 30)

    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ Please set CAMINO_API_KEY environment variable")
        return

    # Using synchronous client
    with CaminoAI(api_key=api_key) as client:
        try:
            response = client.query("pizza places in Brooklyn")
            print(f"✅ Sync query found {response.total} pizza places")

            if response.results:
                first_result = response.results[0]
                print(f"   First result: {first_result.name}")
        except APIError as e:
            print(f"❌ Sync query failed: {e.message}")


if __name__ == "__main__":
    # Run async examples
    asyncio.run(main())

    # Run sync examples
    # sync_examples()
