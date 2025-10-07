"""Tests for Camino AI data models."""

import pytest
from pydantic import ValidationError

from camino_ai.models import (
    APIError,
    AuthenticationError,
    CaminoError,
    Coordinate,
    JourneyRequest,
    QueryRequest,
    QueryResponse,
    QueryResult,
    RateLimitError,
    RelationshipRequest,
    RelationshipResponse,
    RouteSegment,
    TransportMode,
    Waypoint,
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
        constraints = {"transport_mode": TransportMode.DRIVING}
        assert constraints["transport_mode"] == "driving"


class TestQueryModels:
    """Test query-related models."""

    def test_query_request_minimal(self):
        """Test minimal QueryRequest."""
        request = QueryRequest(query="coffee shops")
        assert request.query == "coffee shops"
        assert request.lat is None
        assert request.lon is None
        assert request.radius is None
        assert request.limit == 20  # Default value

    def test_query_request_full(self):
        """Test full QueryRequest with all fields."""
        request = QueryRequest(
            query="coffee shops", lat=40.7831, lon=-73.9712, radius=1000, limit=10
        )
        assert request.query == "coffee shops"
        assert request.lat == 40.7831
        assert request.lon == -73.9712
        assert request.radius == 1000
        assert request.limit == 10

    def test_query_result(self):
        """Test QueryResult model."""
        result = QueryResult(
            id=123,
            type="node",
            location=Coordinate(lat=40.7831, lon=-73.9712),
            tags={"name": "Central Perk", "phone": "555-1234"},
            name="Central Perk",
            amenity="cafe",
            relevance_rank=1,
        )
        assert result.name == "Central Perk"
        assert result.location.lat == 40.7831
        assert result.location.lon == -73.9712
        assert result.amenity == "cafe"
        assert result.tags["phone"] == "555-1234"

    def test_query_response(self):
        """Test QueryResponse model."""
        result = QueryResult(
            id=123,
            type="node",
            location=Coordinate(lat=40.7831, lon=-73.9712),
            tags={"name": "Test Place"},
            name="Test Place",
            relevance_rank=1,
        )
        response = QueryResponse(
            query="test query",
            results=[result],
            ai_ranked=True,
            pagination={
                "total_results": 1,
                "limit": 20,
                "offset": 0,
                "returned_count": 1,
                "has_more": False,
            },
        )
        assert len(response.results) == 1
        assert response.pagination.total_results == 1
        assert response.query == "test query"


class TestRelationshipModels:
    """Test relationship-related models."""

    def test_relationship_request(self):
        """Test RelationshipRequest model."""
        from_loc = Coordinate(lat=40.7831, lon=-73.9712)
        to_loc = Coordinate(lat=40.7589, lon=-73.9851)
        request = RelationshipRequest(start=from_loc, end=to_loc, include=["distance"])
        assert request.start == from_loc
        assert request.end == to_loc
        assert request.include == ["distance"]

    def test_relationship_response(self):
        """Test RelationshipResponse model."""
        response = RelationshipResponse(
            distance="1.2 km",
            direction="northeast",
            walking_time="15 minutes",
            actual_distance_km=1.235,
            duration_seconds=900,
            driving_time="5 minutes",
            description="1.2 km northeast",
        )
        assert response.distance == "1.2 km"
        assert response.direction == "northeast"
        assert response.actual_distance_km == 1.235
        assert response.walking_time == "15 minutes"
        assert response.description == "1.2 km northeast"


class TestJourneyModels:
    """Test journey-related models."""

    def test_waypoint_with_coordinate(self):
        """Test Waypoint with coordinate location."""
        waypoint = Waypoint(lat=40.7831, lon=-73.9712, purpose="Central Park")
        assert waypoint.lat == 40.7831
        assert waypoint.lon == -73.9712
        assert waypoint.purpose == "Central Park"

    def test_waypoint_minimal(self):
        """Test minimal Waypoint."""
        waypoint = Waypoint(lat=40.7831, lon=-73.9712, purpose="Home")
        assert waypoint.lat == 40.7831
        assert waypoint.lon == -73.9712
        assert waypoint.purpose == "Home"

    def test_journey_constraints(self):
        """Test journey constraints as dict."""
        constraints = {
            "transport_mode": TransportMode.DRIVING,
            "max_duration": 120,
            "avoid_tolls": True,
            "avoid_highways": False,
        }
        assert constraints["transport_mode"] == TransportMode.DRIVING
        assert constraints["max_duration"] == 120
        assert constraints["avoid_tolls"] is True
        assert constraints["avoid_highways"] is False

    def test_journey_request(self):
        """Test JourneyRequest model."""
        waypoints = [
            Waypoint(lat=40.7831, lon=-73.9712, purpose="Start"),
            Waypoint(lat=40.7589, lon=-73.9851, purpose="End"),
        ]
        constraints = {"transport_mode": TransportMode.WALKING}
        request = JourneyRequest(waypoints=waypoints, constraints=constraints)
        assert len(request.waypoints) == 2
        assert request.constraints == constraints

    def test_route_segment(self):
        """Test RouteSegment model."""
        start = Coordinate(lat=40.7831, lon=-73.9712)
        end = Coordinate(lat=40.7589, lon=-73.9851)
        segment = RouteSegment(
            start=start,
            end=end,
            distance=1234.56,
            duration=300.0,
            instructions="Turn left on Broadway",
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
        # Should only include non-None values and defaults
        assert data["query"] == "test"
        assert "lat" not in data or data.get("lat") is None
        assert data.get("rank") is True  # default value
        assert data.get("mode") == "basic"  # default value

    def test_include_none_serialization(self):
        """Test that None values are included when requested."""
        request = QueryRequest(query="test")
        data = request.model_dump()
        # Should include all fields
        assert data["query"] == "test"
        assert data["lat"] is None
        assert data["lon"] is None
        assert data["radius"] is None
        assert data["rank"] is True
        assert data["limit"] == 20
        assert data["mode"] == "basic"

    def test_model_validation_from_dict(self):
        """Test model creation from dictionary."""
        data = {
            "query": "test",
            "results": [
                {
                    "id": 123,
                    "type": "node",
                    "location": {"lat": 40.7831, "lon": -73.9712},
                    "tags": {"name": "Test Place"},
                    "name": "Test Place",
                    "relevance_rank": 1,
                }
            ],
            "ai_ranked": True,
            "pagination": {
                "total_results": 1,
                "limit": 20,
                "offset": 0,
                "returned_count": 1,
                "has_more": False,
            },
        }
        response = QueryResponse.model_validate(data)
        assert len(response.results) == 1
        assert response.results[0].name == "Test Place"
        assert response.pagination.total_results == 1
