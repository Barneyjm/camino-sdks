"""Tests for Camino AI data models."""

import pytest
from pydantic import ValidationError

from camino_ai.models import (
    Coordinate,
    QueryRequest,
    QueryResponse,
    QueryResult,
    RelationshipRequest,
    RelationshipResponse,
    RouteSegmentInfo,
    RelationshipAnalysis,
    LocationWithPurpose,
    ContextRequest,
    ContextResponse,
    JourneyRequest,
    JourneyResponse,
    RouteRequest,
    RouteResponse,
    TransportMode,
    Waypoint,
    JourneyConstraints,
    RouteSegment,
    CaminoError,
    APIError,
    AuthenticationError,
    RateLimitError,
)


class TestCoordinate:
    """Test Coordinate model."""
    
    def test_valid_coordinate(self):
        """Test creating a valid coordinate."""
        coord = Coordinate(lat=40.7831, lon=-73.9712)
        assert coord.lat == 40.7831
        assert coord.lon == -73.9712
    
    def test_coordinate_validation(self):
        """Test coordinate validation."""
        # Test missing required fields
        with pytest.raises(ValidationError):
            Coordinate(lat=40.7831)  # Missing lon
        
        with pytest.raises(ValidationError):
            Coordinate(lon=-73.9712)  # Missing lat
    
    def test_coordinate_serialization(self):
        """Test coordinate serialization."""
        coord = Coordinate(lat=40.7831, lon=-73.9712)
        data = coord.model_dump()
        expected = {"lat": 40.7831, "lon": -73.9712}
        assert data == expected


class TestTransportMode:
    """Test TransportMode enum."""
    
    def test_transport_modes(self):
        """Test all transport mode values."""
        assert TransportMode.DRIVING == "driving"
        assert TransportMode.WALKING == "walking"
        assert TransportMode.CYCLING == "cycling"
        assert TransportMode.TRANSIT == "transit"
    
    def test_transport_mode_in_model(self):
        """Test transport mode usage in models."""
        constraints = JourneyConstraints(transport_mode=TransportMode.DRIVING)
        assert constraints.transport_mode == "driving"


class TestQueryModels:
    """Test query-related models."""
    
    def test_query_request_minimal(self):
        """Test minimal QueryRequest."""
        request = QueryRequest(q="coffee shops")
        assert request.q == "coffee shops"
        assert request.lat is None
        assert request.lon is None
        assert request.radius is None
        assert request.limit == 20  # Default value
    
    def test_query_request_full(self):
        """Test full QueryRequest with all fields."""
        request = QueryRequest(
            q="coffee shops",
            lat=40.7831,
            lon=-73.9712,
            radius=1000,
            limit=10
        )
        assert request.q == "coffee shops"
        assert request.lat == 40.7831
        assert request.lon == -73.9712
        assert request.radius == 1000
        assert request.limit == 10
    
    def test_query_result(self):
        """Test QueryResult model."""
        coord = Coordinate(lat=40.7831, lon=-73.9712)
        result = QueryResult(
            name="Central Perk",
            address="123 Coffee St",
            coordinate=coord,
            category="cafe",
            confidence=0.95,
            metadata={"phone": "555-1234"}
        )
        assert result.name == "Central Perk"
        assert result.address == "123 Coffee St"
        assert result.coordinate == coord
        assert result.category == "cafe"
        assert result.confidence == 0.95
        assert result.metadata == {"phone": "555-1234"}
    
    def test_query_response(self):
        """Test QueryResponse model."""
        coord = Coordinate(lat=40.7831, lon=-73.9712)
        result = QueryResult(name="Test Place", coordinate=coord)
        response = QueryResponse(
            results=[result],
            total=1,
            query_id="test-123"
        )
        assert len(response.results) == 1
        assert response.total == 1
        assert response.query_id == "test-123"


class TestRelationshipModels:
    """Test relationship-related models."""
    
    def test_relationship_request(self):
        """Test RelationshipRequest model."""
        from_loc = Coordinate(lat=40.7831, lon=-73.9712)
        to_loc = Coordinate(lat=40.7589, lon=-73.9851)
        request = RelationshipRequest(
            start=from_loc,
            end=to_loc,
            include=["distance"]
        )
        assert request.start == from_loc
        assert request.end == to_loc
        assert request.include == ["distance"]
    
    def test_relationship_response(self):
        """Test RelationshipResponse model."""
        response = RelationshipResponse(
            feasible=True,
            total_distance_km=1.235,
            total_time_minutes=15,
            total_time_formatted="15 minutes",
            transport_mode="walking",
            route_segments=[
                RouteSegmentInfo(
                    from_=LocationWithPurpose(lat=40.7831, lon=-73.9712, purpose="Start"),
                    to=LocationWithPurpose(lat=40.7589, lon=-73.9851, purpose="End"),
                    distance_km=1.235,
                    estimated_time="15 minutes"
                )
            ],
            analysis=RelationshipAnalysis(
                summary="Direct walking route",
                optimization_opportunities=[]
            )
        )
        assert response.feasible == True
        assert response.total_distance_km == 1.235
        assert response.total_time_minutes == 15
        assert response.transport_mode == "walking"
        assert len(response.route_segments) == 1
        assert response.analysis.summary == "Direct walking route"
        # Test backward compatibility
        assert response.distance == 1235.0  # meters
        assert response.relationship == "Direct walking route"


class TestJourneyModels:
    """Test journey-related models."""
    
    def test_waypoint_with_coordinate(self):
        """Test Waypoint with coordinate location."""
        coord = Coordinate(lat=40.7831, lon=-73.9712)
        waypoint = Waypoint(
            location=coord,
            stop_duration=15,
            arrival_time="2024-01-01T10:00:00Z"
        )
        assert waypoint.location == coord
        assert waypoint.stop_duration == 15
        assert waypoint.arrival_time == "2024-01-01T10:00:00Z"
    
    def test_waypoint_with_address(self):
        """Test Waypoint with string address."""
        waypoint = Waypoint(location="123 Main St, New York, NY")
        assert waypoint.location == "123 Main St, New York, NY"
    
    def test_journey_constraints(self):
        """Test JourneyConstraints model."""
        constraints = JourneyConstraints(
            transport_mode=TransportMode.DRIVING,
            max_duration=120,
            avoid_tolls=True,
            avoid_highways=False
        )
        assert constraints.transport_mode == TransportMode.DRIVING
        assert constraints.max_duration == 120
        assert constraints.avoid_tolls is True
        assert constraints.avoid_highways is False
    
    def test_journey_request(self):
        """Test JourneyRequest model."""
        waypoints = [
            Waypoint(location=Coordinate(lat=40.7831, lon=-73.9712)),
            Waypoint(location=Coordinate(lat=40.7589, lon=-73.9851))
        ]
        constraints = JourneyConstraints(transport_mode=TransportMode.WALKING)
        request = JourneyRequest(
            waypoints=waypoints,
            constraints=constraints,
            optimize=True
        )
        assert len(request.waypoints) == 2
        assert request.constraints == constraints
        assert request.optimize is True
    
    def test_route_segment(self):
        """Test RouteSegment model."""
        start = Coordinate(lat=40.7831, lon=-73.9712)
        end = Coordinate(lat=40.7589, lon=-73.9851)
        segment = RouteSegment(
            start=start,
            end=end,
            distance=1234.56,
            duration=300.0,
            instructions="Turn left on Broadway"
        )
        assert segment.start == start
        assert segment.end == end
        assert segment.distance == 1234.56
        assert segment.duration == 300.0
        assert segment.instructions == "Turn left on Broadway"


class TestExceptionModels:
    """Test exception classes."""
    
    def test_camino_error_basic(self):
        """Test basic CaminoError."""
        error = CaminoError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.details == {}
    
    def test_camino_error_with_details(self):
        """Test CaminoError with details."""
        details = {"code": "TEST_ERROR", "field": "query"}
        error = CaminoError("Validation failed", details)
        assert error.message == "Validation failed"
        assert error.details == details
    
    def test_api_error(self):
        """Test APIError."""
        response = {"error": "Bad request", "code": "INVALID_PARAMS"}
        error = APIError("Request failed", 400, response)
        assert error.message == "Request failed"
        assert error.status_code == 400
        assert error.response == response
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid API key", 401)
        assert isinstance(error, APIError)
        assert error.message == "Invalid API key"
        assert error.status_code == 401
    
    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError("Too many requests", 60)
        assert isinstance(error, APIError)
        assert error.message == "Too many requests"
        assert error.retry_after == 60


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_exclude_none_serialization(self):
        """Test that None values are excluded from serialization."""
        request = QueryRequest(query="test")
        data = request.model_dump(exclude_none=True)
        expected = {"query": "test"}
        assert data == expected
    
    def test_include_none_serialization(self):
        """Test that None values are included when requested."""
        request = QueryRequest(query="test")
        data = request.model_dump()
        expected = {
            "query": "test",
            "location": None,
            "radius": None,
            "limit": None
        }
        assert data == expected
    
    def test_model_validation_from_dict(self):
        """Test model creation from dictionary."""
        data = {
            "results": [
                {
                    "name": "Test Place",
                    "coordinate": {"lat": 40.7831, "lon": -73.9712}
                }
            ],
            "total": 1
        }
        response = QueryResponse.model_validate(data)
        assert len(response.results) == 1
        assert response.results[0].name == "Test Place"
        assert response.total == 1