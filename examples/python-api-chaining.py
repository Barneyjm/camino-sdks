#!/usr/bin/env python3
"""
Advanced API Chaining Example for Camino AI Python SDK

This example demonstrates how to chain multiple Camino AI endpoints together
to create intelligent location-based workflows:

1. /context - Discover POIs around a location
2. /query - Get detailed information about each POI  
3. /journey - Plan an optimized route through selected POIs

Use cases:
- Planning food tours
- Finding nearby services along a route
- Discovering attractions in an area
- Creating personalized itineraries
"""

import asyncio
import os
from typing import List, Dict, Any
from dataclasses import dataclass

from camino_ai import (
    CaminoAI,
    ContextRequest,
    QueryRequest, 
    JourneyRequest,
    RelationshipRequest,
    Coordinate,
    Waypoint,
    JourneyConstraints,
    TransportMode,
    APIError,
)


@dataclass
class POIDetails:
    """Enhanced POI information from query results."""
    name: str
    coordinate: Coordinate
    address: str = ""
    category: str = ""
    confidence: float = 0.0
    context_distance: float = 0.0
    query_details: Dict[str, Any] = None


class LocationChainWorkflow:
    """A workflow class for chaining Camino AI APIs together."""
    
    def __init__(self, api_key: str):
        self.client = CaminoAI(api_key=api_key)
        self.verbose = True
    
    async def discover_area_pois(
        self, 
        location: Coordinate, 
        radius: int = 1000,
        categories: List[str] = None
    ) -> List[str]:
        """
        Step 1: Use /context to discover POIs in an area.
        Returns a list of POI names/types found in the area.
        """
        if self.verbose:
            print(f"🔍 Discovering POIs around {location.lat:.4f}, {location.lon:.4f}")
        
        try:
            context_request = ContextRequest(
                location=location,
                radius=f"{radius}m",
                context=f"Find interesting places within {radius} meters"
            )
            
            context_response = await self.client.context_async(context_request)
            
            # Extract POI names from context - this would depend on the actual API response structure
            # For now, we'll simulate based on nearby results
            poi_names = []
            if hasattr(context_response, 'nearby') and context_response.nearby:
                poi_names = [poi.name for poi in context_response.nearby[:10]]  # Limit to top 10
            
            # If no nearby POIs in context, generate some common ones based on categories
            if not poi_names and categories:
                poi_names = [f"{category}s near me" for category in categories]
            elif not poi_names:
                # Default fallback POI types
                poi_names = ["restaurants", "cafes", "attractions", "shopping"]
            
            if self.verbose:
                print(f"   Found {len(poi_names)} POI types: {', '.join(poi_names[:3])}...")
                
            return poi_names
            
        except APIError as e:
            if self.verbose:
                print(f"❌ Context discovery failed: {e.message}")
            return ["restaurants", "cafes"]  # Fallback
    
    async def query_poi_details(
        self, 
        poi_names: List[str], 
        location: Coordinate,
        radius: int = 1000,
        limit_per_query: int = 3
    ) -> List[POIDetails]:
        """
        Step 2: Use /query to get detailed information about each POI type.
        Returns enriched POI details with locations and metadata.
        """
        if self.verbose:
            print(f"📍 Querying details for {len(poi_names)} POI types...")
        
        all_pois = []
        
        for poi_name in poi_names:
            try:
                query_request = QueryRequest(
                    q=f"{poi_name} near {location.lat}, {location.lon}",
                    lat=location.lat,
                    lon=location.lon,
                    radius=radius,
                    limit=limit_per_query
                )
                
                query_response = await self.client.query_async(query_request)
                
                if query_response.results:
                    for result in query_response.results:
                        # Calculate distance from original location
                        try:
                            relationship = await self.client.relationship_async(
                                RelationshipRequest(
                                    start=location,
                                    to=result.coordinate,
                                    include=["distance"]
                                )
                            )
                            distance = relationship.distance
                        except:
                            distance = 0.0
                        
                        poi_detail = POIDetails(
                            name=result.name,
                            coordinate=result.coordinate,
                            address=result.address or "",
                            category=result.category or poi_name,
                            confidence=result.confidence or 0.0,
                            context_distance=distance,
                            query_details=result.metadata or {}
                        )
                        all_pois.append(poi_detail)
                        
                        if self.verbose and len(all_pois) <= 5:  # Show first few
                            print(f"   • {poi_detail.name} ({poi_detail.category}) - {distance:.0f}m")
                
            except APIError as e:
                if self.verbose:
                    print(f"⚠️ Query failed for '{poi_name}': {e.message}")
                continue
        
        if self.verbose:
            print(f"   Total POIs found: {len(all_pois)}")
            
        return all_pois
    
    async def plan_optimal_journey(
        self, 
        start_location: Coordinate,
        pois: List[POIDetails], 
        transport_mode: TransportMode = TransportMode.WALKING,
        max_stops: int = 5
    ) -> Dict[str, Any]:
        """
        Step 3: Use /journey to plan an optimized route through selected POIs.
        Returns journey details with optimized route and timing.
        """
        if not pois:
            return {"error": "No POIs available for journey planning"}
        
        # Select best POIs based on confidence and distance
        selected_pois = self._select_best_pois(pois, max_stops)
        
        if self.verbose:
            print(f"🗺️ Planning journey through {len(selected_pois)} stops...")
            for i, poi in enumerate(selected_pois, 1):
                print(f"   {i}. {poi.name} ({poi.context_distance:.0f}m)")
        
        try:
            # Create waypoints for journey
            waypoints = [
                # Start location
                Waypoint(
                    location=start_location,
                    purpose="start"
                )
            ]
            
            # Add POI waypoints
            for poi in selected_pois:
                waypoints.append(
                    Waypoint(
                        location=poi.coordinate,
                        purpose=f"visit:{poi.category}"
                    )
                )
            
            journey_request = JourneyRequest(
                waypoints=waypoints,
                constraints=JourneyConstraints(
                    transport=transport_mode.value,
                    time_budget="2h",  # 2 hour budget
                    preferences=["scenic", "safe"]
                )
            )
            
            journey_response = await self.client.journey_async(journey_request)
            
            journey_summary = {
                "total_distance": journey_response.total_distance,
                "total_duration": journey_response.total_duration,
                "transport_mode": transport_mode.value,
                "stops": len(selected_pois),
                "selected_pois": [
                    {
                        "name": poi.name,
                        "category": poi.category,
                        "coordinate": {"lat": poi.coordinate.lat, "lon": poi.coordinate.lon},
                        "confidence": poi.confidence
                    }
                    for poi in selected_pois
                ],
                "segments": [
                    {
                        "distance": segment.distance,
                        "duration": segment.duration,
                        "instructions": segment.instructions
                    }
                    for segment in journey_response.segments
                ],
                "optimized_order": getattr(journey_response, 'optimized_order', None)
            }
            
            if self.verbose:
                print(f"✅ Journey planned successfully:")
                print(f"   Total distance: {journey_response.total_distance/1000:.1f} km")
                print(f"   Total duration: {journey_response.total_duration/60:.0f} minutes")
                print(f"   Segments: {len(journey_response.segments)}")
            
            return journey_summary
            
        except APIError as e:
            if self.verbose:
                print(f"❌ Journey planning failed: {e.message}")
            return {"error": f"Journey planning failed: {e.message}"}
    
    def _select_best_pois(self, pois: List[POIDetails], max_stops: int) -> List[POIDetails]:
        """Select the best POIs based on confidence, distance, and diversity."""
        # Sort by confidence and proximity
        sorted_pois = sorted(
            pois, 
            key=lambda x: (x.confidence * 0.7 + (1000 - min(x.context_distance, 1000)) / 1000 * 0.3), 
            reverse=True
        )
        
        # Ensure diversity by limiting same categories
        selected = []
        categories_used = set()
        
        for poi in sorted_pois:
            if len(selected) >= max_stops:
                break
                
            # Prefer diverse categories, but allow duplicates if confidence is very high
            if poi.category not in categories_used or poi.confidence > 0.9:
                selected.append(poi)
                categories_used.add(poi.category)
        
        return selected
    
    async def run_complete_workflow(
        self,
        location: Coordinate,
        categories: List[str] = None,
        radius: int = 1000,
        transport_mode: TransportMode = TransportMode.WALKING,
        max_stops: int = 5
    ) -> Dict[str, Any]:
        """
        Run the complete workflow: context → query → journey
        """
        print("🌍 Starting Complete Location Intelligence Workflow")
        print("=" * 55)
        
        # Step 1: Discover POIs in area
        poi_names = await self.discover_area_pois(
            location=location,
            radius=radius,
            categories=categories
        )
        
        # Step 2: Get detailed information about POIs
        poi_details = await self.query_poi_details(
            poi_names=poi_names,
            location=location,
            radius=radius,
            limit_per_query=2
        )
        
        # Step 3: Plan optimized journey
        journey_plan = await self.plan_optimal_journey(
            start_location=location,
            pois=poi_details,
            transport_mode=transport_mode,
            max_stops=max_stops
        )
        
        return {
            "workflow_summary": {
                "start_location": {"lat": location.lat, "lon": location.lon},
                "poi_types_discovered": len(poi_names),
                "total_pois_found": len(poi_details),
                "journey_planned": "error" not in journey_plan
            },
            "discovered_poi_types": poi_names,
            "poi_details": [
                {
                    "name": poi.name,
                    "category": poi.category, 
                    "distance_from_start": poi.context_distance,
                    "confidence": poi.confidence
                }
                for poi in poi_details
            ],
            "journey_plan": journey_plan
        }
    
    async def close(self):
        """Clean up resources."""
        await self.client.aclose()


async def example_food_tour_planning():
    """Example: Plan a food tour in Manhattan"""
    print("\n🍽️ Example: Food Tour Planning in Manhattan")
    print("-" * 45)
    
    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ Please set CAMINO_API_KEY environment variable")
        return
    
    workflow = LocationChainWorkflow(api_key)
    
    # Manhattan location (near Washington Square Park)
    manhattan_location = Coordinate(lat=40.7308, lng=-73.9973)
    
    result = await workflow.run_complete_workflow(
        location=manhattan_location,
        categories=["restaurants", "cafes", "bakeries", "food markets"],
        radius=800,  # 800 meter radius
        transport_mode=TransportMode.WALKING,
        max_stops=4
    )
    
    print("\n📊 Workflow Results:")
    print(f"• POI types discovered: {result['workflow_summary']['poi_types_discovered']}")
    print(f"• Total POIs found: {result['workflow_summary']['total_pois_found']}")
    print(f"• Journey planned: {'✅' if result['workflow_summary']['journey_planned'] else '❌'}")
    
    if result['workflow_summary']['journey_planned']:
        journey = result['journey_plan']
        print(f"• Food tour distance: {journey['total_distance']/1000:.1f} km")
        print(f"• Estimated duration: {journey['total_duration']/60:.0f} minutes")
        print(f"• Number of stops: {journey['stops']}")
        
        print("\n🎯 Selected Food Stops:")
        for i, poi in enumerate(journey['selected_pois'], 1):
            print(f"   {i}. {poi['name']} ({poi['category']}) - Confidence: {poi['confidence']:.2f}")
    
    await workflow.close()


async def example_business_area_analysis():
    """Example: Analyze business services in an area"""
    print("\n🏢 Example: Business Area Analysis in Financial District")  
    print("-" * 55)
    
    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ Please set CAMINO_API_KEY environment variable")
        return
    
    workflow = LocationChainWorkflow(api_key)
    
    # Financial District, NYC
    financial_district = Coordinate(lat=40.7074, lng=-74.0113)
    
    result = await workflow.run_complete_workflow(
        location=financial_district,
        categories=["banks", "law offices", "business services", "coworking"],
        radius=500,
        transport_mode=TransportMode.WALKING,
        max_stops=3
    )
    
    print("\n📈 Business Analysis Results:")
    print(f"• Service types found: {len(result['discovered_poi_types'])}")
    print(f"• Total businesses: {result['workflow_summary']['total_pois_found']}")
    
    # Show top businesses by category
    business_by_category = {}
    for poi in result['poi_details']:
        category = poi['category']
        if category not in business_by_category:
            business_by_category[category] = []
        business_by_category[category].append(poi)
    
    print("\n🏛️ Top Businesses by Category:")
    for category, businesses in business_by_category.items():
        print(f"\n   {category.title()}:")
        for business in sorted(businesses, key=lambda x: x['confidence'], reverse=True)[:2]:
            print(f"   • {business['name']} (confidence: {business['confidence']:.2f})")
    
    await workflow.close()


async def main():
    """Run all workflow examples."""
    print("🚀 Camino AI - API Chaining Workflow Examples")
    print("=" * 50)
    
    # Run food tour example
    await example_food_tour_planning()
    
    # Run business analysis example  
    await example_business_area_analysis()
    
    print("\n✨ All workflow examples completed!")


if __name__ == "__main__":
    asyncio.run(main())