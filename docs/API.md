# Camino AI API Reference

Complete API reference for the Camino AI SDKs.

## Table of Contents

- [Authentication](#authentication)
- [Client Configuration](#client-configuration)
- [Query API](#query-api)
- [Relationship API](#relationship-api)
- [Context API](#context-api)
- [Journey API](#journey-api)
- [Route API](#route-api)
- [Error Handling](#error-handling)
- [Data Models](#data-models)

## Authentication

All API requests require authentication using an API key. Get your API key from the [Camino AI Dashboard](https://app.getcamino.ai).

### Python
```python
from camino_ai import CaminoAI

client = CaminoAI(api_key="your-api-key-here")
```

### JavaScript/TypeScript
```typescript
import { CaminoAI } from '@camino-ai/sdk';

const client = new CaminoAI({ apiKey: 'your-api-key-here' });
```

## Client Configuration

### Python
```python
client = CaminoAI(
    api_key="your-api-key",
    base_url="https://api.getcamino.ai",  # Default
    timeout=30.0,                        # Seconds
    max_retries=3,                       # Number of retries
    retry_backoff=1.0                    # Backoff multiplier
)
```

### JavaScript/TypeScript
```typescript
const client = new CaminoAI({
  apiKey: 'your-api-key',
  baseURL: 'https://api.getcamino.ai', // Default
  timeout: 30000,                      // Milliseconds
  maxRetries: 3,                       // Number of retries
  retryBackoff: 1000                   // Backoff in milliseconds
});
```

## Query API

Search for points of interest using natural language queries.

### Basic Query

**Python**
```python
# Simple string query
response = client.query("coffee shops near Central Park")

# Advanced query with parameters
from camino_ai import QueryRequest, Coordinate

response = client.query(QueryRequest(
    query="Italian restaurants",
    location=Coordinate(lat=40.7831, lng=-73.9712),
    radius=1000,  # meters
    limit=10
))

# Async version
response = await client.query_async("pizza places in Brooklyn")
```

**JavaScript/TypeScript**
```typescript
// Simple string query
const response = await client.query('coffee shops near Central Park');

// Advanced query with parameters
const response = await client.query({
  query: 'Italian restaurants',
  location: { lat: 40.7831, lng: -73.9712 },
  radius: 1000, // meters
  limit: 10
});
```

### Response Format
```json
{
  "results": [
    {
      "name": "Joe's Coffee",
      "address": "123 Broadway, New York, NY",
      "coordinate": { "lat": 40.7831, "lng": -73.9712 },
      "category": "cafe",
      "confidence": 0.95,
      "metadata": {
        "phone": "+1-555-0123",
        "website": "https://joescoffee.com"
      }
    }
  ],
  "total": 1,
  "queryId": "query_123456789"
}
```

## Relationship API

Calculate spatial relationships between two locations.

### Calculate Distance & Bearing

**Python**
```python
from camino_ai import RelationshipRequest, Coordinate

response = client.relationship(RelationshipRequest(
    from_location=Coordinate(lat=40.7831, lng=-73.9712),  # Central Park
    to_location=Coordinate(lat=40.7589, lng=-73.9851),    # Times Square
    relationship_type="distance_and_bearing"
))

print(f"Distance: {response.distance}m")
print(f"Bearing: {response.bearing}°")
print(f"Relationship: {response.relationship}")

# Async version
response = await client.relationship_async(request)
```

**JavaScript/TypeScript**
```typescript
const response = await client.relationship({
  fromLocation: { lat: 40.7831, lng: -73.9712 }, // Central Park
  toLocation: { lat: 40.7589, lng: -73.9851 },   // Times Square
  relationshipType: 'distance_and_bearing'
});

console.log(`Distance: ${response.distance}m`);
console.log(`Bearing: ${response.bearing}°`);
console.log(`Relationship: ${response.relationship}`);
```

### Response Format
```json
{
  "distance": 1234.56,
  "bearing": 156.8,
  "relationship": "southeast",
  "metadata": {
    "walkingTime": 900,
    "drivingTime": 300
  }
}
```

## Context API

Get rich contextual information about any location.

### Get Location Context

**Python**
```python
from camino_ai import ContextRequest, Coordinate

response = client.context(ContextRequest(
    location=Coordinate(lat=40.7831, lng=-73.9712),
    radius=500,  # meters
    categories=["restaurant", "entertainment", "shopping"]
))

print(f"Area: {response.context.get('area')}")
print(f"Nearby places: {len(response.nearby)}")

# Async version
response = await client.context_async(request)
```

**JavaScript/TypeScript**
```typescript
const response = await client.context({
  location: { lat: 40.7831, lng: -73.9712 },
  radius: 500, // meters
  categories: ['restaurant', 'entertainment', 'shopping']
});

console.log(`Area: ${response.context.area}`);
console.log(`Nearby places: ${response.nearby?.length || 0}`);
```

### Response Format
```json
{
  "location": { "lat": 40.7831, "lng": -73.9712 },
  "context": {
    "area": "Manhattan",
    "neighborhood": "Upper West Side",
    "zipCode": "10024",
    "density": "high",
    "walkScore": 95
  },
  "nearby": [
    {
      "name": "Lincoln Center",
      "coordinate": { "lat": 40.7722, "lng": -73.9838 },
      "category": "entertainment",
      "distance": 450
    }
  ]
}
```

## Journey API

Plan optimized multi-waypoint journeys.

### Multi-Waypoint Journey

**Python**
```python
from camino_ai import (
    JourneyRequest, 
    Waypoint, 
    JourneyConstraints, 
    TransportMode,
    Coordinate
)

response = client.journey(JourneyRequest(
    waypoints=[
        Waypoint(location=Coordinate(lat=40.7831, lng=-73.9712)),
        Waypoint(location="Times Square, New York"),
        Waypoint(location=Coordinate(lat=40.7505, lng=-73.9934))
    ],
    constraints=JourneyConstraints(
        transport_mode=TransportMode.DRIVING,
        max_duration=60,  # minutes
        avoid_tolls=True
    ),
    optimize=True
))

print(f"Total distance: {response.total_distance}m")
print(f"Total duration: {response.total_duration}s")
print(f"Optimized order: {response.optimized_order}")

# Async version
response = await client.journey_async(request)
```

**JavaScript/TypeScript**
```typescript
const response = await client.journey({
  waypoints: [
    { location: { lat: 40.7831, lng: -73.9712 } },
    { location: 'Times Square, New York' },
    { location: { lat: 40.7505, lng: -73.9934 } }
  ],
  constraints: {
    transportMode: 'driving',
    maxDuration: 60, // minutes
    avoidTolls: true
  },
  optimize: true
});

console.log(`Total distance: ${response.totalDistance}m`);
console.log(`Total duration: ${response.totalDuration}s`);
console.log(`Optimized order: ${response.optimizedOrder}`);
```

### Response Format
```json
{
  "totalDistance": 5432.1,
  "totalDuration": 1200.5,
  "segments": [
    {
      "start": { "lat": 40.7831, "lng": -73.9712 },
      "end": { "lat": 40.7589, "lng": -73.9851 },
      "distance": 2716.05,
      "duration": 600.25,
      "instructions": "Head south on Broadway for 0.8 miles"
    }
  ],
  "optimizedOrder": [0, 1, 2]
}
```

## Route API

Calculate point-to-point routes with turn-by-turn directions.

### Simple Route

**Python**
```python
from camino_ai import RouteRequest, TransportMode, Coordinate

response = client.route(RouteRequest(
    start=Coordinate(lat=40.7831, lng=-73.9712),
    end=Coordinate(lat=40.7589, lng=-73.9851),
    transport_mode=TransportMode.WALKING,
    avoid_highways=True
))

print(f"Route distance: {response.distance}m")
print(f"Route duration: {response.duration}s")
print(f"Number of segments: {len(response.segments)}")

# Async version
response = await client.route_async(request)
```

**JavaScript/TypeScript**
```typescript
const response = await client.route({
  start: { lat: 40.7831, lng: -73.9712 },
  end: { lat: 40.7589, lng: -73.9851 },
  transportMode: 'walking',
  avoidHighways: true
});

console.log(`Route distance: ${response.distance}m`);
console.log(`Route duration: ${response.duration}s`);
console.log(`Number of segments: ${response.segments.length}`);
```

### Response Format
```json
{
  "distance": 2716.05,
  "duration": 1800.5,
  "segments": [
    {
      "start": { "lat": 40.7831, "lng": -73.9712 },
      "end": { "lat": 40.7720, "lng": -73.9820 },
      "distance": 850.2,
      "duration": 600.0,
      "instructions": "Head southeast on West 77th Street"
    }
  ],
  "polyline": "encoded_polyline_string_here"
}
```

## Error Handling

All SDKs provide comprehensive error handling with specific exception types.

### Python Error Handling
```python
from camino_ai import (
    CaminoAI, 
    APIError, 
    AuthenticationError, 
    RateLimitError
)

try:
    client = CaminoAI(api_key="invalid-key")
    response = client.query("coffee shops")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    # Handle invalid API key
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after: {e.retry_after}s")
    # Implement backoff and retry
except APIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
    # Handle other API errors
```

### JavaScript/TypeScript Error Handling
```typescript
import { 
  CaminoAI, 
  APIError, 
  AuthenticationError, 
  RateLimitError,
  NetworkError,
  TimeoutError 
} from '@camino-ai/sdk';

try {
  const client = new CaminoAI({ apiKey: 'invalid-key' });
  const response = await client.query('coffee shops');
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error(`Authentication failed: ${error.message}`);
    // Handle invalid API key
  } else if (error instanceof RateLimitError) {
    console.error(`Rate limit exceeded. Retry after: ${error.retryAfter}s`);
    // Implement backoff and retry
  } else if (error instanceof NetworkError) {
    console.error(`Network error: ${error.message}`);
    // Handle network issues
  } else if (error instanceof TimeoutError) {
    console.error(`Request timed out: ${error.message}`);
    // Handle timeouts
  } else if (error instanceof APIError) {
    console.error(`API error: ${error.message} (status: ${error.statusCode})`);
    // Handle other API errors
  }
}
```

## Data Models

### Transport Modes
- `driving` - Car/automobile transportation
- `walking` - Pedestrian directions
- `cycling` - Bicycle directions
- `transit` - Public transportation

### Coordinate
```json
{
  "lat": 40.7831,  // Latitude in decimal degrees
  "lng": -73.9712  // Longitude in decimal degrees
}
```

### Common Response Fields

All API responses may include:
- Standard data fields as documented above
- `metadata` - Additional contextual information
- Timestamps and identifiers where relevant
- Confidence scores for AI-powered features

## Rate Limits

- **Free Tier**: 1,000 requests/month, 10 requests/minute
- **Pro Tier**: 10,000 requests/month, 100 requests/minute  
- **Enterprise**: Custom limits

When rate limits are exceeded, the API returns a `429` status code with a `Retry-After` header indicating when to retry.

## Best Practices

1. **Caching**: Cache responses when appropriate to reduce API calls
2. **Error Handling**: Always implement comprehensive error handling
3. **Retry Logic**: Use exponential backoff for retries (built into SDKs)
4. **Validation**: Validate coordinates and other inputs before API calls
5. **Monitoring**: Monitor your API usage and response times
6. **Security**: Keep your API key secure and rotate it regularly