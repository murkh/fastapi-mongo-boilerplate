# FastAPI MongoDB Boilerplate

A production-ready FastAPI boilerplate with Motor (MongoDB async driver) using best practices and clean architecture principles.

## Features

- **FastAPI** with async/await support
- **Motor** for MongoDB async operations
- **Repository Pattern** for clean data access
- **Service Layer** for business logic
- **Pydantic** for data validation
- **Type Hints** throughout the codebase
- **SOLID Principles** implementation
- **Clean Architecture** with separation of concerns
- **Health Check** endpoints
- **Prometheus Metrics** integration
- **Environment-based** configuration
- **Docker** support

## Architecture

```
src/app/
├── api/                    # API routes
│   └── v1/               # API version 1
│       ├── health.py     # Health check endpoints
│       └── users.py      # User endpoints
├── core/                  # Core application setup
│   ├── config.py         # Configuration management
│   ├── database.py       # Database connection
│   ├── error_handler.py  # Global error handling
│   └── setup.py          # Application factory
├── models/               # Pydantic models
│   ├── base.py          # Base model with MongoDB ObjectId
│   └── user.py          # User models
├── repositories/         # Data access layer
│   ├── base.py          # Base repository with CRUD operations
│   └── user.py          # User-specific repository
├── services/            # Business logic layer
│   └── user.py          # User service
└── main.py              # Application entry point
```

## Quick Start

### Prerequisites

- Python 3.12+
- MongoDB (local or cloud)
- uv (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastapi-mongo-boilerplate
   ```

2. **Install dependencies**
   ```bash
   uv sync
   # or
   pip install -e .
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection string
   ```

4. **Run the application**
   ```bash
   uv run uvicorn src.app.main:app --reload
   # or
   python -m uvicorn src.app.main:app --reload
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Application
APP_NAME=FastAPI MongoDB Boilerplate
APP_DESCRIPTION=FastAPI boilerplate with Motor (MongoDB async driver)
APP_VERSION=0.1.0

# Environment
ENVIRONMENT=local
DEBUG=true

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=fastapi_boilerplate
MONGODB_MAX_POOL_SIZE=10
MONGODB_MIN_POOL_SIZE=1
```

## API Endpoints

### Health Check
- `GET /api/v1/health/` - Application health check
- `GET /api/v1/health/db` - Database health check

### Users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/` - Get all users (with pagination)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users/by-email/{email}` - Get user by email
- `GET /api/v1/users/by-username/{username}` - Get user by username
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user
- `GET /api/v1/users/count/total` - Get total user count

## Development

### Code Quality

The project uses several tools for code quality:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking

```bash
# Format code
uv run black src/
uv run isort src/

# Lint code
uv run flake8 src/

# Type checking
uv run mypy src/
```

### Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Best Practices Implemented

### SOLID Principles
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Base repository can be extended without modification
- **Liskov Substitution**: Repository implementations are interchangeable
- **Interface Segregation**: Clean interfaces for different concerns
- **Dependency Inversion**: High-level modules don't depend on low-level modules

### Clean Architecture
- **API Layer**: Handles HTTP requests/responses
- **Service Layer**: Contains business logic
- **Repository Layer**: Handles data access
- **Model Layer**: Defines data structures

### Repository Pattern
- Abstracts data access logic
- Makes testing easier with dependency injection
- Provides consistent interface for CRUD operations
- Separates business logic from data access

### Error Handling
- Global exception handlers
- Proper HTTP status codes
- Consistent error response format
- Validation error handling

### Configuration Management
- Environment-based configuration
- Type-safe settings with Pydantic
- Default values for development
- Secure handling of secrets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run code quality checks
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
