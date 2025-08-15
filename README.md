# Camino AI SDKs

Official SDKs for [Camino AI](https://getcamino.ai) - Guide your AI agents through the real world with location intelligence, spatial reasoning, and route planning.

[![CI](https://github.com/camino-ai/camino-sdks/workflows/CI/badge.svg)](https://github.com/camino-ai/camino-sdks/actions)
[![Python Package](https://img.shields.io/pypi/v/camino-ai-sdk.svg)](https://pypi.org/project/camino-ai-sdk/)
[![npm Package](https://img.shields.io/npm/v/@camino-ai/sdk.svg)](https://www.npmjs.com/package/@camino-ai/sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌍 What is Camino AI?

Camino AI provides location intelligence and spatial reasoning capabilities for AI agents. Our API enables developers to build applications that can:

- 🔍 **Search places** using natural language queries
- 📍 **Calculate spatial relationships** between locations  
- 🗺️ **Get rich context** about any location
- 🧭 **Plan optimized journeys** with multiple waypoints
- 🛤️ **Generate routes** with turn-by-turn directions

## 📦 Available SDKs

| Language | Package | Documentation | Version |
|----------|---------|---------------|---------|
| **Python** | [`camino-ai-sdk`](https://pypi.org/project/camino-ai-sdk/) | [Python Docs](python/README.md) | ![PyPI](https://img.shields.io/pypi/v/camino-ai-sdk.svg) |
| **JavaScript/TypeScript** | [`@camino-ai/sdk`](https://www.npmjs.com/package/@camino-ai/sdk) | [JS/TS Docs](javascript/README.md) | ![npm](https://img.shields.io/npm/v/@camino-ai/sdk.svg) |

## 🚀 Quick Start

### Python

```bash
pip install camino-ai-sdk
```

```python
from camino_ai import CaminoAI

client = CaminoAI(api_key="your-api-key")

# Search for places
response = client.query("coffee shops near Central Park")
for result in response.results:
    print(f"{result.name}: {result.address}")

# Calculate relationships  
relationship = client.relationship({
    "from": {"lat": 40.7831, "lng": -73.9712},
    "to": {"lat": 40.7589, "lng": -73.9851}
})
print(f"Distance: {relationship.distance}m")
```

### JavaScript/TypeScript

```bash
npm install @camino-ai/sdk
```

```typescript
import { CaminoAI } from '@camino-ai/sdk';

const client = new CaminoAI({ apiKey: 'your-api-key' });

// Search for places
const response = await client.query('coffee shops near Central Park');
response.results.forEach(result => {
    console.log(`${result.name}: ${result.address}`);
});

// Calculate relationships
const relationship = await client.relationship({
    from: { lat: 40.7831, lng: -73.9712 },
    to: { lat: 40.7589, lng: -73.9851 }
});
console.log(`Distance: ${relationship.distance}m`);
```

## 🎯 Key Features

### 🔍 Natural Language Queries
```python
# Python
response = client.query("Italian restaurants with outdoor seating in SoHo")

# JavaScript  
const response = await client.query("Italian restaurants with outdoor seating in SoHo");
```

### 📍 Spatial Intelligence
```python
# Python
relationship = client.relationship({
    "from": {"lat": 40.7831, "lng": -73.9712},
    "to": {"lat": 40.7589, "lng": -73.9851}
})

# JavaScript
const relationship = await client.relationship({
    from: { lat: 40.7831, lng: -73.9712 },
    to: { lat: 40.7589, lng: -73.9851 }
});
```

### 🗺️ Rich Context
```python
# Python
context = client.context({
    "location": {"lat": 40.7831, "lng": -73.9712},
    "radius": 500
})

# JavaScript
const context = await client.context({
    location: { lat: 40.7831, lng: -73.9712 },
    radius: 500
});
```

### 🧭 Journey Optimization
```python
# Python
journey = client.journey({
    "waypoints": [
        {"location": {"lat": 40.7831, "lng": -73.9712}},
        {"location": {"lat": 40.7589, "lng": -73.9851}}
    ],
    "optimize": True
})

# JavaScript
const journey = await client.journey({
    waypoints: [
        { location: { lat: 40.7831, lng: -73.9712 } },
        { location: { lat: 40.7589, lng: -73.9851 } }
    ],
    optimize: true
});
```

## 📖 Documentation

- **[API Reference](docs/API.md)** - Complete API documentation
- **[Python SDK](python/README.md)** - Python-specific documentation
- **[JavaScript SDK](javascript/README.md)** - JavaScript/TypeScript documentation
- **[Examples](examples/)** - Code examples and tutorials

## 🛠️ Examples

| Example | Python | JavaScript | TypeScript |
|---------|--------|------------|------------|
| **Basic Usage** | [python-basic.py](examples/python-basic.py) | [javascript-basic.js](examples/javascript-basic.js) | - |
| **Advanced Patterns** | - | - | [typescript-advanced.ts](examples/typescript-advanced.ts) |
| **Error Handling** | ✅ Included | ✅ Included | ✅ Included |
| **Async/Await** | ✅ Included | ✅ Included | ✅ Included |

## 🔧 Development

This repository uses a monorepo structure with automated SDK generation from OpenAPI specifications.

### Structure
```
camino-sdks/
├── python/              # Python SDK
├── javascript/          # JavaScript/TypeScript SDK  
├── openapi/            # OpenAPI specifications
├── docs/               # Shared documentation
├── examples/           # Code examples
├── tools/              # Build and generation tools
└── .github/            # CI/CD workflows
```

### Building

```bash
# Install dependencies
npm install

# Generate SDKs from OpenAPI spec
npm run generate

# Build all packages
npm run build

# Run tests
npm run test
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/camino-ai/camino-sdks/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/camino-ai/camino-sdks/discussions)
- **Email Support**: [support@getcamino.ai](mailto:support@getcamino.ai)
- **Documentation**: [docs.getcamino.ai](https://docs.getcamino.ai)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Website**: [getcamino.ai](https://getcamino.ai)
- **API Documentation**: [docs.getcamino.ai](https://docs.getcamino.ai)  
- **Dashboard**: [app.getcamino.ai](https://app.getcamino.ai)
- **Status Page**: [status.getcamino.ai](https://status.getcamino.ai)

---

<div align="center">
  <p>Built with ❤️ by the <a href="https://getcamino.ai">Camino AI</a> team</p>
  <p>
    <a href="https://twitter.com/getcamino">Twitter</a> •
    <a href="https://github.com/camino-ai">GitHub</a> •
    <a href="https://linkedin.com/company/camino-ai">LinkedIn</a>
  </p>
</div>
