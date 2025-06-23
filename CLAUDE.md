# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI Redis Queue (RQ) background job processing demo that demonstrates how to handle long-running tasks asynchronously using a distributed architecture. The project includes three types of background tasks:

1. **CPU-intensive tasks**: Prime number generation and Fibonacci calculation
2. **I/O-intensive tasks**: Weather API calls to OpenWeatherMap

## Architecture

The project uses a microservices architecture with three main components:

- **FastAPI Web Application** (`main.py`): REST API that enqueues tasks and provides status endpoints
- **Redis Queue Worker** (`worker.py`): Background process that executes tasks from the queue
- **Redis Server**: Message broker and result storage

### Key Files

- **main.py**: FastAPI application with task enqueuing and status endpoints
- **worker.py**: RQ worker process that consumes and executes background tasks
- **tasks.py**: Background task implementations:
  - `find_primes_in_range()`: CPU-intensive prime number generation
  - `calculate_fibonacci()`: Recursive Fibonacci calculation (slow for n>30)
  - `fetch_weather_for_cities_sync()`: Weather API calls for multiple cities
- **demo.py**: Standalone script to test task functions directly (bypasses queue)
- **docker-compose.yml**: Orchestrates all services (Redis, FastAPI, Worker)

## Development Commands

### Using Docker Compose (Recommended)

```bash
# Start all services (Redis, FastAPI app, RQ worker)
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Rebuild and restart
docker compose up --build -d
```

### Local Development

```bash
# Install dependencies
uv sync

# Start Redis server (in separate terminal)
redis-server

# Start FastAPI application (in separate terminal)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start RQ worker (in separate terminal)
python worker.py

# Run demonstration script (direct task execution)
python demo.py
```

## API Endpoints

The FastAPI application provides the following endpoints:

- `GET /` - API information and available endpoints
- `GET /health` - Health check with Redis connectivity status
- `POST /tasks/primes` - Enqueue prime number generation task
  ```json
  {"start": 1, "end": 10000}
  ```
- `POST /tasks/fibonacci` - Enqueue Fibonacci calculation task
  ```json
  {"n": 35}
  ```
- `POST /tasks/weather` - Enqueue weather data fetching task (no body required)
- `GET /tasks/{task_id}` - Get task status and results

### Example Usage

```bash
# Enqueue a prime number task
curl -X POST "http://localhost:8000/tasks/primes" \
  -H "Content-Type: application/json" \
  -d '{"start": 1, "end": 10000}'

# Check task status
curl "http://localhost:8000/tasks/{task_id}"

# Health check
curl "http://localhost:8000/health"
```

## Environment Setup

- Copy `.env.example` to `.env` and add your OpenWeatherMap API key
- Set `OPENWEATHER_API_KEY` environment variable for weather tasks
- Redis connection is configured via `REDIS_HOST` and `REDIS_PORT` environment variables

## Key Dependencies

- **FastAPI**: Web framework for REST API
- **Redis/RQ**: Background job queue processing
- **aiohttp**: Async HTTP client for weather API calls
- **python-dotenv**: Environment variable management
- **uvicorn**: ASGI server for FastAPI

## Task Performance Characteristics

- Prime generation: 3-10 seconds for ranges like 1-100000
- Fibonacci calculation: Gets slow around n=35-40, taking several seconds
- Weather fetching: 5-15 seconds for 15 cities with API rate limiting

## Workflow

1. Client sends POST request to enqueue a task
2. FastAPI app adds task to Redis queue and returns task_id
3. RQ worker picks up task from queue and executes it
4. Client polls GET /tasks/{task_id} to check status and get results
5. Results are stored in Redis and returned when task completes

## Development Notes

- If the project uses `uv` then we should add modules using `ud add <module>` rather than `pip install <module>`

## Commit Message Guidelines

- When creating commit messages, always create a good comprehensive commit message
- Please do not add references to Claude Code like `Generated with Claude Code` or `Co-Authored-By: Claude noreply@anthropic.com`