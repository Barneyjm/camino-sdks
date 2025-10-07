"""Tests for the Camino AI Python client."""


import pytest
from pytest_httpx import HTTPXMock

from camino_ai import CaminoAI
from camino_ai.models import (
    APIError,
    AuthenticationError,
    ContextRequest,
    ContextResponse,
    Coordinate,
    QueryRequest,
    QueryResponse,
    RateLimitError,
    RelationshipRequest,
    RelationshipResponse,
)


class TestCaminoAI:
    """Test suite for CaminoAI client."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.client = CaminoAI(api_key=self.api_key)

    def test_init_with_defaults(self):
        """Test client initialization with default values."""
        client = CaminoAI(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.getcamino.ai"
        assert client.timeout == 30.0
        assert client.max_retries == 3
        assert client.retry_backoff == 1.0

    def test_init_with_custom_values(self):
        """Test client initialization with custom values."""
        client = CaminoAI(
            api_key="test-key",
            base_url="https://custom.api.com",
            timeout=60.0,
            max_retries=5,
            retry_backoff=2.0,
        )
        assert client.api_key == "test-key"
        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.retry_backoff == 2.0

    def test_headers_configuration(self):
        """Test that headers are properly configured."""
        client = CaminoAI(api_key="test-key")
        expected_headers = {
            "X-API-Key": "test-key",
            "Content-Type": "application/json",
            "User-Agent": "camino-ai-python/0.1.0",
        }
        assert client._headers == expected_headers


class TestQueryMethods:
    """Test query-related methods."""

    def setup_method(self):
        self.client = CaminoAI(api_key="test-api-key")

    def test_query_with_string(self, httpx_mock: HTTPXMock):
        """Test query method with string input."""
        mock_response = {
            "query": "coffee shops",
            "results": [
                {
                    "id": 123,
                    "type": "node",
                    "location": {"lat": 40.7831, "lon": -73.9712},
                    "tags": {"name": "Central Perk", "amenity": "cafe"},
                    "name": "Central Perk",
                    "amenity": "cafe",
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

        httpx_mock.add_response(
            method="GET",
            url="https://api.getcamino.ai/query?query=coffee+shops&rank=true&limit=20&offset=0&answer=false&mode=basic",
            json=mock_response,
        )

        response = self.client.query("coffee shops")

        assert isinstance(response, QueryResponse)
        assert len(response.results) == 1
        assert response.results[0].name == "Central Perk"
        assert response.pagination.total_results == 1

    def test_query_with_request_object(self, httpx_mock: HTTPXMock):
        """Test query method with QueryRequest object."""
        mock_response = {
            "query": "coffee shops",
            "results": [],
            "ai_ranked": True,
            "pagination": {
                "total_results": 0,
                "limit": 10,
                "offset": 0,
                "returned_count": 0,
                "has_more": False,
            },
        }

        httpx_mock.add_response(
            method="GET",
            url="https://api.getcamino.ai/query?query=coffee+shops&lat=40.7831&lon=-73.9712&radius=1000&rank=true&limit=10&offset=0&answer=false&mode=basic",
            json=mock_response,
        )

        request = QueryRequest(
            query="coffee shops", lat=40.7831, lon=-73.9712, radius=1000, limit=10
        )

        response = self.client.query(request)
        assert isinstance(response, QueryResponse)
        assert response.pagination.total_results == 0

    @pytest.mark.asyncio
    async def test_query_async(self, httpx_mock: HTTPXMock):
        """Test async query method."""
        mock_response = {
            "query": "test query",
            "results": [],
            "ai_ranked": True,
            "pagination": {
                "total_results": 0,
                "limit": 20,
                "offset": 0,
                "returned_count": 0,
                "has_more": False,
            },
        }

        httpx_mock.add_response(
            method="GET",
            url="https://api.getcamino.ai/query?query=test+query&rank=true&limit=20&offset=0&answer=false&mode=basic",
            json=mock_response,
        )

        response = await self.client.query_async("test query")
        assert isinstance(response, QueryResponse)
        assert response.pagination.total_results == 0


class TestRelationshipMethods:
    """Test relationship-related methods."""

    def setup_method(self):
        self.client = CaminoAI(api_key="test-api-key")

    def test_relationship(self, httpx_mock: HTTPXMock):
        """Test relationship method."""
        mock_response = {
            "distance": "1.2 km",
            "direction": "southwest",
            "walking_time": "15 minutes",
            "actual_distance_km": 1.235,
            "duration_seconds": 900,
            "driving_time": "5 minutes",
            "description": "The location is 1.2 km southwest, approximately 15 minutes walking",
        }

        httpx_mock.add_response(
            method="POST",
            url="https://api.getcamino.ai/relationship",
            json=mock_response,
        )

        request = RelationshipRequest(
            start=Coordinate(lat=40.7831, lon=-73.9712),
            end=Coordinate(lat=40.7589, lon=-73.9851),
        )

        response = self.client.relationship(request)
        assert isinstance(response, RelationshipResponse)
        assert response.distance == "1.2 km"
        assert response.direction == "southwest"
        assert response.walking_time == "15 minutes"
        assert response.actual_distance_km == 1.235
        assert response.duration_seconds == 900
        assert response.driving_time == "5 minutes"
        assert "1.2 km southwest" in response.description


class TestContextMethods:
    """Test context-related methods."""

    def setup_method(self):
        self.client = CaminoAI(api_key="test-api-key")

    def test_context(self, httpx_mock: HTTPXMock):
        """Test context method."""
        mock_response = {
            "area_description": "Upper West Side neighborhood in Manhattan, characterized by residential buildings and cultural institutions",
            "relevant_places": {
                "restaurants": ["The Smith", "Cafe Luxembourg"],
                "hotels": ["The Beacon Hotel"],
                "services": ["UPS Store", "CVS Pharmacy"],
                "transportation": ["72nd Street Subway Station"],
                "shops": ["Zabar's", "Fairway Market"],
                "attractions": ["Museum of Natural History"],
                "leisure": ["Central Park"],
                "offices": [],
            },
            "location": {"lat": 40.7831, "lon": -73.9712},
            "search_radius": 500,
            "total_places_found": 47,
        }

        httpx_mock.add_response(
            method="POST", url="https://api.getcamino.ai/context", json=mock_response
        )

        request = ContextRequest(
            location=Coordinate(lat=40.7831, lon=-73.9712), radius=500
        )

        response = self.client.context(request)
        assert isinstance(response, ContextResponse)
        assert response.location.lat == 40.7831
        assert response.location.lon == -73.9712
        assert response.search_radius == 500
        assert response.total_places_found == 47
        assert "Upper West Side" in response.area_description
        assert len(response.relevant_places.restaurants) == 2


class TestErrorHandling:
    """Test error handling and exception raising."""

    def setup_method(self):
        self.client = CaminoAI(api_key="test-api-key")

    def test_authentication_error(self, httpx_mock: HTTPXMock):
        """Test authentication error handling."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.getcamino.ai/query?query=test&rank=true&limit=20&offset=0&answer=false&mode=basic",
            status_code=401,
            json={"message": "Invalid API key"},
        )

        with pytest.raises(AuthenticationError) as exc_info:
            self.client.query("test")

        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value)

    def test_rate_limit_error(self, httpx_mock: HTTPXMock):
        """Test rate limit error handling."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.getcamino.ai/query?query=test&rank=true&limit=20&offset=0&answer=false&mode=basic",
            status_code=429,
            headers={"Retry-After": "60"},
            json={"message": "Rate limit exceeded"},
        )

        with pytest.raises(RateLimitError) as exc_info:
            self.client.query("test")

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    def test_generic_api_error(self, httpx_mock: HTTPXMock):
        """Test generic API error handling."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.getcamino.ai/query?query=test&rank=true&limit=20&offset=0&answer=false&mode=basic",
            status_code=500,
            json={"message": "Internal server error"},
        )

        with pytest.raises(APIError) as exc_info:
            self.client.query("test")

        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)


class TestContextManagers:
    """Test context manager functionality."""

    def test_sync_context_manager(self):
        """Test synchronous context manager."""
        with CaminoAI(api_key="test-key") as client:
            assert client.api_key == "test-key"

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test asynchronous context manager."""
        async with CaminoAI(api_key="test-key") as client:
            assert client.api_key == "test-key"
