"""Data models for the Camino AI SDK."""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, model_validator


class Coordinate(BaseModel):
    """Geographic coordinate with latitude and longitude."""

    lat: float = Field(...,
                       description="Latitude in decimal degrees", ge=-90, le=90)
    lon: float = Field(...,
                       description="Longitude in decimal degrees", ge=-180, le=180)

    @property
    def lng(self) -> float:
        """Alias for lon for backward compatibility."""
        return self.lon


class TransportMode(str, Enum):
    """Available transport modes for routing."""

    DRIVING = "driving"
    WALKING = "walking"
    CYCLING = "cycling"
    TRANSIT = "transit"


class QueryRequest(BaseModel):
    """Request model for natural language location queries.

    Supports temporal queries to search historical OpenStreetMap data:
    - Point in time: time="2020-01-01"
    - Changes since: time="2020.."
    - Changes between: time="2020..2024"

    Either 'query' or 'osm_ids' must be provided.
    """

    query: Optional[str] = Field(None,
                       description="Natural language query, e.g., 'coffee near me'")
    lat: Optional[float] = Field(
        None, description="Latitude for the center of your search")
    lon: Optional[float] = Field(
        None, description="Longitude for the center of your search")
    radius: Optional[int] = Field(
        None, description="Search radius in meters. Only used if lat/lon are provided.")
    rank: Optional[bool] = Field(
        True, description="Use AI to rank results by relevance (default: true)")
    limit: Optional[int] = Field(
        20, description="Maximum number of results to return (1-100, default: 20)", ge=1, le=100)
    offset: Optional[int] = Field(
        0, description="Number of results to skip for pagination (default: 0)", ge=0)
    answer: Optional[bool] = Field(
        False, description="Generate a human-readable answer summary (default: false)")
    time: Optional[str] = Field(
        None, description="Time parameter for temporal queries: '2020-01-01' (point), '2020..' (since), '2020..2024' (range)")
    osm_ids: Optional[str] = Field(
        None, description="Comma-separated OSM IDs to query specific elements (e.g., 'node/123,way/456')")
    mode: Optional[str] = Field(
        "basic", description="Query mode: 'basic' (open data only) or 'advanced' (web enrichment, AWS fallback)")

    @model_validator(mode='after')
    def validate_query_or_osm_ids(self):
        """Ensure that either query or osm_ids is provided."""
        if not self.query and not self.osm_ids:
            raise ValueError("Either 'query' or 'osm_ids' must be provided")
        return self


class QueryResult(BaseModel):
    """Individual result from a query."""

    id: int = Field(..., description="Unique identifier for the location")
    type: str = Field(..., description="OSM type (node, way, relation)")
    location: Coordinate = Field(..., description="Geographic coordinates")
    tags: Dict[str, Any] = Field(..., description="OSM tags for the location")
    name: str = Field(..., description="Name of the location")
    amenity: Optional[str] = Field(None, description="Type of amenity")
    cuisine: Optional[str] = Field(
        None, description="Cuisine type if applicable")
    relevance_rank: int = Field(..., description="AI relevance ranking")

    # Web enrichment field (optional, added when TAVILY_API_KEY is configured)
    web_enrichment: Optional[WebEnrichment] = Field(
        None,
        description="Web verification and operational status signals from authoritative sources"
    )

    @property
    def coordinate(self) -> Coordinate:
        """Alias for location field for backward compatibility."""
        return self.location

    @property
    def category(self) -> Optional[str]:
        """Extract category from amenity or cuisine for backward compatibility."""
        return self.amenity or self.cuisine

    @property
    def address(self) -> Optional[str]:
        """Extract address from tags if available."""
        # Try to construct address from various tag fields
        addr_parts = []
        if 'addr:housenumber' in self.tags:
            addr_parts.append(self.tags['addr:housenumber'])
        if 'addr:street' in self.tags:
            addr_parts.append(self.tags['addr:street'])
        if 'addr:city' in self.tags:
            addr_parts.append(self.tags['addr:city'])
        return ' '.join(addr_parts) if addr_parts else None

    @property
    def confidence(self) -> float:
        """Calculate confidence score based on relevance rank."""
        # Convert relevance rank to confidence score (rank 1 = 1.0, rank 10 = 0.1)
        return max(0.1, 1.0 - (self.relevance_rank - 1) * 0.1)

    @property
    def metadata(self) -> Dict[str, Any]:
        """Return tags as metadata."""
        return self.tags


class Pagination(BaseModel):
    """Pagination information for query results."""

    total_results: int = Field(...,
                               description="Total number of results available")
    limit: int = Field(..., description="Maximum results per page")
    offset: int = Field(..., description="Current offset")
    returned_count: int = Field(...,
                                description="Number of results in this response")
    has_more: bool = Field(...,
                           description="Whether more results are available")
    next_offset: Optional[int] = Field(
        None, description="Offset for next page")


class QueryResponse(BaseModel):
    """Response model for location queries."""

    query: str = Field(..., description="The original query string")
    results: List[QueryResult] = Field(..., description="Query results")
    ai_ranked: bool = Field(..., description="Whether results were AI-ranked")
    pagination: Pagination = Field(..., description="Pagination information")
    answer: Optional[str] = Field(
        None, description="AI-generated answer summary")
    historical_context: Optional[str] = Field(
        None, description="Human-readable temporal context (e.g., 'as of January 1, 2020', 'changes since March 2020')")
    diff_analysis: Optional['DiffAnalysis'] = Field(
        None, description="Analysis of changes for temporal diff queries")

    @property
    def total(self) -> int:
        """Alias for pagination.total_results for backward compatibility."""
        return self.pagination.total_results


class RelationshipRequest(BaseModel):
    """Request model for spatial relationship queries."""

    start: Coordinate = Field(..., description="Starting location")
    end: Coordinate = Field(..., description="Target location")
    include: Optional[List[str]] = Field(
        default=["distance", "direction", "travel_time", "description"],
        description="List of relationship aspects to include in response"
    )


class LocationWithPurpose(BaseModel):
    """Location with purpose information."""

    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    purpose: str = Field(..., description="Purpose of this location")


class RouteSegmentInfo(BaseModel):
    """Route segment in relationship response."""

    from_: LocationWithPurpose = Field(...,
                                       alias="from", description="Starting point")
    to: LocationWithPurpose = Field(..., description="Ending point")
    distance_km: float = Field(..., description="Distance in kilometers")
    estimated_time: str = Field(...,
                                description="Estimated time as formatted string")

    model_config = {"populate_by_name": True}


class RelationshipAnalysis(BaseModel):
    """Analysis section of relationship response."""

    summary: str = Field(..., description="Summary of the route analysis")
    optimization_opportunities: List[str] = Field(
        ..., description="List of optimization suggestions")


class RelationshipResponse(BaseModel):
    """Response model for spatial relationships."""

    distance: str = Field(..., description="Formatted distance string")
    direction: str = Field(..., description="Direction from start to end")
    walking_time: str = Field(..., description="Formatted walking time")
    actual_distance_km: float = Field(...,
                                      description="Actual distance in kilometers")
    duration_seconds: float = Field(..., description="Duration in seconds")
    driving_time: str = Field(..., description="Formatted driving time")
    description: str = Field(..., description="Human-readable description")


class ContextRequest(BaseModel):
    """Request model for location context.

    Supports temporal queries to analyze how areas have changed over time:
    - Point in time: time="2020-01-01"
    - Changes since: time="2020.."
    - Changes between: time="2018..2024"
    """

    location: Coordinate = Field(...,
                                 description="Location to get context for")
    radius: Optional[int] = Field(
        None, description="Context radius in meters (e.g., 500, 1000)")
    context: Optional[str] = Field(
        None, description="Context description for what to find")
    categories: Optional[List[str]] = Field(
        None, description="Specific categories to include")
    time: Optional[str] = Field(
        None, description="Time parameter for temporal queries: '2020-01-01' (point), '2020..' (since), '2020..2024' (range)")


class DiffAnalysis(BaseModel):
    """Analysis of changes for temporal diff queries."""

    added: List[Dict[str, Any]] = Field(..., description="Places added during time period")
    removed: List[Dict[str, Any]] = Field(..., description="Places removed during time period")
    modified: List[Dict[str, Any]] = Field(..., description="Places modified during time period")
    summary: str = Field(..., description="Summary of changes")
    total_changes: int = Field(..., description="Total number of changes detected")


class TemporalAnalysis(BaseModel):
    """Analysis of area changes over time for context queries."""

    summary: str = Field(..., description="Summary of area evolution")
    total_changes: int = Field(..., description="Total number of changes")
    changes_breakdown: Dict[str, int] = Field(..., description="Breakdown of changes by type")
    category_trends: Dict[str, Dict[str, int]] = Field(..., description="Changes by category")
    trends: List[str] = Field(..., description="Major trends identified")
    notable_changes: List[str] = Field(..., description="Notable changes in the area")
    character_change: Optional[str] = Field(None, description="How the area character has changed")
    detailed_changes: Dict[str, List[Dict[str, Any]]] = Field(..., description="Detailed list of changes")


class RelevantPlaces(BaseModel):
    """Categorized relevant places in the context area."""

    restaurants: Optional[List[str]] = Field(default=[], description="Restaurant names")
    hotels: Optional[List[str]] = Field(default=[], description="Hotel names")
    services: Optional[List[str]] = Field(default=[], description="Service establishment names")
    transportation: Optional[List[str]] = Field(default=[], description="Transportation options")
    shops: Optional[List[str]] = Field(default=[], description="Shop names")
    attractions: Optional[List[str]] = Field(default=[], description="Attraction names")
    leisure: Optional[List[str]] = Field(default=[], description="Leisure facilities")
    offices: Optional[List[str]] = Field(default=[], description="Office buildings")


class ContextResponse(BaseModel):
    """Response model for location context."""

    area_description: str = Field(..., description="Description of the area")
    relevant_places: RelevantPlaces = Field(...,
                                            description="Categorized places in the area")
    location: Coordinate = Field(..., description="Queried location")
    search_radius: int = Field(..., description="Search radius used in meters")
    total_places_found: int = Field(...,
                                    description="Total number of places found")
    context_insights: Optional[str] = Field(
        None, description="Context-specific insights based on the provided context")
    historical_context: Optional[str] = Field(
        None, description="Human-readable temporal context (e.g., 'as of January 1, 2020', 'changes since March 2020')")
    temporal_analysis: Optional['TemporalAnalysis'] = Field(
        None, description="Analysis of area changes over time for temporal queries")


class Waypoint(BaseModel):
    """Waypoint for journey planning."""

    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    purpose: str = Field(..., description="Purpose of this waypoint")


class JourneyRequest(BaseModel):
    """Request model for multi-waypoint journey planning."""

    waypoints: List[Waypoint] = Field(..., description="Journey waypoints")
    constraints: Optional[Dict[str, Any]] = Field(
        None, description="Journey constraints like transport mode and time budget")


class RouteSegment(BaseModel):
    """Individual route segment for backward compatibility."""

    start: Coordinate = Field(..., description="Segment start coordinate")
    end: Coordinate = Field(..., description="Segment end coordinate")
    distance: float = Field(..., description="Segment distance in meters")
    duration: float = Field(..., description="Segment duration in seconds")
    instructions: Optional[str] = Field(
        None, description="Turn-by-turn instructions")


class JourneyResponse(BaseModel):
    """Response model for journey planning."""

    feasible: bool = Field(..., description="Whether the journey is feasible")
    total_distance_km: float = Field(...,
                                     description="Total journey distance in kilometers")
    total_time_minutes: int = Field(...,
                                    description="Total journey time in minutes")
    total_time_formatted: str = Field(...,
                                      description="Formatted total time string")
    transport_mode: str = Field(..., description="Transport mode used")
    route_segments: List[RouteSegmentInfo] = Field(
        ..., description="Journey route segments")
    analysis: RelationshipAnalysis = Field(...,
                                           description="Route analysis and optimization")


class RouteRequest(BaseModel):
    """Request model for point-to-point routing."""

    start_lat: float = Field(..., description="Starting latitude")
    start_lon: float = Field(..., description="Starting longitude")
    end_lat: float = Field(..., description="Ending latitude")
    end_lon: float = Field(..., description="Ending longitude")
    mode: Optional[str] = Field(
        "foot", description="Transport mode (foot, car, bicycle)")
    include_geometry: Optional[bool] = Field(
        True, description="Include route geometry")


class RouteSummary(BaseModel):
    """Summary information for a route."""

    total_distance_meters: float = Field(...,
                                         description="Total distance in meters")
    total_duration_seconds: float = Field(...,
                                          description="Total duration in seconds")


class RouteResponse(BaseModel):
    """Response model for routing."""

    summary: RouteSummary = Field(..., description="Route summary")
    instructions: List[str] = Field(...,
                                    description="Turn-by-turn instructions")
    geometry: Optional[Dict[str, Any]] = Field(
        None, description="Route geometry data")
    include_geometry: bool = Field(...,
                                   description="Whether geometry was included")


class WebEnrichment(BaseModel):
    """Web verification data for a place - focuses on validation not extraction.

    Provides signals about a place's web presence and operational status
    by checking authoritative sources like Yelp, TripAdvisor, etc.
    """

    web_verified: bool = Field(False, description="Whether the place was found on the web")
    verification_sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of web sources that mention this place (domain, title, score)"
    )
    recent_mentions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recent web mentions with snippets (snippet, url, score)"
    )
    appears_operational: Optional[bool] = Field(
        None,
        description="Operational status: True=likely open, False=likely closed, None=unknown"
    )
    confidence: str = Field(
        "low",
        description="Confidence level of operational status: low, medium, high"
    )


class SearchRequest(BaseModel):
    """Request model for place searches using Nominatim.

    Supports two modes:
    1. Free-form search: Use the 'query' parameter for natural language searches
    2. Structured search: Use address components for precise location searches

    Note: Cannot combine 'query' with structured parameters.
    """

    # Free-form search parameter
    query: Optional[str] = Field(None,
        description="Free-form search query (e.g., 'Eiffel Tower'). Cannot be combined with structured parameters.")

    # Structured address parameters
    amenity: Optional[str] = Field(None,
        description="Name and/or type of POI (e.g., 'restaurant', 'Starbucks')")
    street: Optional[str] = Field(None,
        description="Street name with optional housenumber (e.g., '123 Main Street')")
    city: Optional[str] = Field(None,
        description="City name (e.g., 'Paris', 'New York')")
    county: Optional[str] = Field(None,
        description="County name")
    state: Optional[str] = Field(None,
        description="State or province name (e.g., 'California', 'Ontario')")
    country: Optional[str] = Field(None,
        description="Country name (e.g., 'France', 'United States')")
    postalcode: Optional[str] = Field(None,
        description="Postal/ZIP code (e.g., '10001', '75001')")

    # Common parameters
    limit: Optional[int] = Field(10,
        description="Maximum number of results to return (1-50, default: 10)", ge=1, le=50)
    mode: Optional[str] = Field(
        "basic", description="Search mode: 'basic' (open data only) or 'advanced' (web enrichment, AWS fallback)")

    @model_validator(mode='after')
    def validate_search_mode(self):
        """Ensure proper usage of free-form vs structured search."""
        structured_params = [
            self.amenity, self.street, self.city,
            self.county, self.state, self.country, self.postalcode
        ]
        has_structured = any(param is not None for param in structured_params)

        if self.query and has_structured:
            raise ValueError("Cannot combine 'query' with structured address parameters")

        if not self.query and not has_structured:
            raise ValueError("Must provide either 'query' or at least one structured address parameter")

        return self


class SearchResult(BaseModel):
    """Individual search result from Nominatim."""

    display_name: str = Field(...,
                              description="Full display name of the location")
    lat: float = Field(..., description="Latitude of the location")
    lon: float = Field(..., description="Longitude of the location")
    type: str = Field(..., description="Type/category of the location")
    importance: float = Field(...,
                              description="Importance score of the result")
    source: str = Field(default="nominatim", description="Data source")
    address: Optional[Dict[str, str]] = Field(None,
                              description="Detailed address components (amenity, house_number, road, city, state, postcode, country, etc.)")

    # Web enrichment fields (optional, added when TAVILY_API_KEY is configured)
    web_enrichment: Optional[WebEnrichment] = Field(
        None,
        description="Web verification and operational status signals from authoritative sources"
    )

    # Street imagery fields (optional, added when include_photos=true)
    street_photos: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Street-level photos from OpenStreetCam if available"
    )
    visual_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Visual context analysis from street imagery"
    )
    has_street_imagery: Optional[bool] = Field(
        None,
        description="Whether street-level imagery is available for this location"
    )


class SearchResponse(BaseModel):
    """Response model for search results."""

    results: List[SearchResult] = Field(...,
                                        description="List of search results")


# Exception classes
class CaminoError(Exception):
    """Base exception for Camino AI SDK."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class APIError(CaminoError):
    """API-related error."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, response)
        self.status_code = status_code
        self.response = response


class AuthenticationError(APIError):
    """Authentication failed."""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after
