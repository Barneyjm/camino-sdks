#!/usr/bin/env python3
"""
Workflow Helpers Example - Camino AI Python SDK

This example shows how to use the built-in workflow helpers to easily
chain APIs together with minimal code. Perfect for common use cases!
"""

import asyncio
import os
from camino_ai import (
    CaminoAI, 
    AreaExplorer, 
    QuickChain,
    Coordinate,
)


async def example_1_area_explorer():
    """Example 1: Use AreaExplorer for complete area exploration workflow."""
    
    print("🗺️ Example 1: Area Explorer Workflow")
    print("-" * 40)
    
    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ Please set CAMINO_API_KEY environment variable")
        return
    
    async with CaminoAI(api_key=api_key) as client:
        # Create area explorer
        explorer = AreaExplorer(client)
        
        # Times Square location
        times_square = Coordinate(lat=40.7589, lng=-73.9851)
        
        # Run complete exploration workflow in one call!
        result = await explorer.explore_and_plan(
            location=times_square,
            poi_types=["restaurants", "theaters", "attractions", "shopping"],
            radius=800,  # 800 meters
            max_journey_stops=4,
            transport_mode="walking"
        )
        
        if result.success:
            print("✅ Area exploration successful!")
            print(f"   📍 Total POIs found: {result.total_pois_found}")
            print(f"   🎯 Journey stops: {len(result.selected_pois)}")
            print(f"   📏 Journey distance: {result.journey_distance/1000:.1f} km")
            print(f"   ⏱️  Journey duration: {result.journey_duration/60:.0f} minutes")
            
            print("\n🎯 Selected stops for your journey:")
            for i, poi in enumerate(result.selected_pois, 1):
                confidence_str = f" (confidence: {poi.confidence:.2f})" if poi.confidence > 0 else ""
                print(f"   {i}. {poi.name} ({poi.category}){confidence_str}")
                
        else:
            print(f"❌ Exploration failed: {result.error_message}")


async def example_2_quick_chain():
    """Example 2: Use QuickChain for simple chaining operations."""
    
    print("\n⚡ Example 2: Quick Chain Operations")
    print("-" * 35)
    
    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ Please set CAMINO_API_KEY environment variable")
        return
    
    async with CaminoAI(api_key=api_key) as client:
        # Create quick chain helper
        quick = QuickChain(client)
        
        # SoHo, NYC
        soho_location = Coordinate(lat=40.7230, lng=-74.0030)
        
        # ==========================================
        # Quick Pattern 1: Context → Query chaining
        # ==========================================
        print("🔍 Pattern 1: Context → Query chaining")
        
        try:
            # This automatically gets area context, then queries for cafes
            cafe_results = await quick.context_to_query(
                location=soho_location,
                poi_type="artisanal coffee shops",
                radius=600
            )
            
            print(f"   Found {len(cafe_results)} coffee shops:")
            for cafe in cafe_results[:3]:  # Show first 3
                print(f"   • {cafe.name}")
                
        except Exception as e:
            print(f"   ❌ Context→Query failed: {e}")
        
        # ==========================================  
        # Quick Pattern 2: Query → Journey chaining
        # ==========================================
        print("\n🧭 Pattern 2: Query → Journey chaining")
        
        try:
            # First, get some art galleries in SoHo
            from camino_ai import QueryRequest
            
            query_request = QueryRequest(
                q="art galleries and museums in SoHo",
                lat=soho_location.lat,
                lon=soho_location.lon,
                radius=500,
                limit=6
            )
            
            query_response = await client.query_async(query_request)
            print(f"   Queried and found {len(query_response.results)} art venues")
            
            # Now chain directly to journey planning
            if query_response.results:
                journey_plan = await quick.query_to_journey(
                    start_location=soho_location,
                    query_results=query_response.results,
                    transport_mode="walking",
                    max_stops=3
                )
                
                print("   ✅ Art gallery tour planned:")
                print(f"   📏 Tour distance: {journey_plan['total_distance']/1000:.1f} km")
                print(f"   ⏱️  Tour duration: {journey_plan['total_duration']/60:.0f} minutes")
                
                print("   🎨 Gallery stops:")
                for i, poi in enumerate(journey_plan['selected_pois'], 1):
                    print(f"      {i}. {poi['name']}")
                    
        except Exception as e:
            print(f"   ❌ Query→Journey failed: {e}")


async def example_3_custom_food_tour():
    """Example 3: Custom food tour using workflow helpers."""
    
    print("\n🍽️ Example 3: Custom Food Tour")
    print("-" * 30)
    
    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ Please set CAMINO_API_KEY environment variable")
        return
    
    async with CaminoAI(api_key=api_key) as client:
        explorer = AreaExplorer(client)
        
        # Little Italy, NYC  
        little_italy = Coordinate(lat=40.7193, lng=-73.9969)
        
        # Create a food-focused exploration
        result = await explorer.explore_and_plan(
            location=little_italy,
            poi_types=[
                "Italian restaurants", 
                "authentic pizzerias",
                "gelato shops",
                "Italian bakeries",
                "wine bars"
            ],
            radius=400,  # Smaller radius for focused area
            max_pois_per_type=2,  # 2 of each type
            max_journey_stops=5,
            transport_mode="walking"
        )
        
        if result.success:
            print("🇮🇹 Little Italy food tour planned!")
            print(f"   🍝 Food stops: {len(result.selected_pois)}")
            print(f"   🚶 Walking distance: {result.journey_distance:.0f} meters")
            print(f"   ⏱️  Estimated time: {result.journey_duration/60:.0f} minutes")
            
            print("\n🍴 Your Italian food adventure:")
            food_emojis = {"Italian restaurants": "🍝", "pizzerias": "🍕", 
                          "gelato": "🍨", "bakeries": "🥖", "wine": "🍷"}
            
            for i, poi in enumerate(result.selected_pois, 1):
                emoji = next((emoji for key, emoji in food_emojis.items() 
                            if key in poi.category.lower()), "🍽️")
                distance = f" ({poi.distance_from_origin:.0f}m from start)" if poi.distance_from_origin > 0 else ""
                print(f"   {i}. {emoji} {poi.name}{distance}")
                
        else:
            print(f"❌ Food tour planning failed: {result.error_message}")


async def example_4_business_district_analysis():
    """Example 4: Analyze a business district for services."""
    
    print("\n🏢 Example 4: Business District Analysis")
    print("-" * 40)
    
    api_key = os.getenv("CAMINO_API_KEY")
    if not api_key:
        print("❌ Please set CAMINO_API_KEY environment variable")
        return
    
    async with CaminoAI(api_key=api_key) as client:
        explorer = AreaExplorer(client)
        
        # Midtown Manhattan
        midtown = Coordinate(lat=40.7549, lng=-73.9840)
        
        # Analyze business services in the area
        result = await explorer.explore_and_plan(
            location=midtown,
            poi_types=[
                "coworking spaces",
                "business centers", 
                "meeting rooms",
                "office supplies",
                "professional services",
                "corporate lunch spots"
            ],
            radius=600,
            max_journey_stops=4,
            transport_mode="walking"
        )
        
        if result.success:
            print("💼 Business district analysis complete!")
            print(f"   🏢 Business services found: {result.total_pois_found}")
            print(f"   📍 Recommended stops: {len(result.selected_pois)}")
            
            # Group by category
            by_category = {}
            for poi in result.selected_pois:
                category = poi.category
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(poi)
            
            print("\n🎯 Top business services by category:")
            for category, pois in by_category.items():
                print(f"   📂 {category.title()}:")
                for poi in pois:
                    confidence_str = f" (confidence: {poi.confidence:.1f})" if poi.confidence > 0 else ""
                    print(f"      • {poi.name}{confidence_str}")
                    
        else:
            print(f"❌ Business analysis failed: {result.error_message}")


async def main():
    """Run all workflow helper examples."""
    
    print("🔗 Camino AI - Workflow Helpers Examples")
    print("=" * 45)
    print("These examples show how easy it is to chain APIs together!")
    
    # Run all examples
    await example_1_area_explorer()
    await example_2_quick_chain() 
    await example_3_custom_food_tour()
    await example_4_business_district_analysis()
    
    print("\n✨ All workflow examples completed!")
    print("\n💡 Key Benefits of Workflow Helpers:")
    print("   • ⚡ Simple one-line API chaining")
    print("   • 🧠 Built-in intelligence for POI selection")
    print("   • 🛡️  Automatic error handling and fallbacks")
    print("   • 🎯 Optimized results based on relevance and distance")


if __name__ == "__main__":
    asyncio.run(main())