# FastAPI Redis Queue Background Job Processing Demo

A comprehensive demonstration of asynchronous background job processing using **FastAPI**, **Redis Queue (RQ)**, and **Docker**. This project showcases how to handle long-running tasks without blocking your web application's response time.

## 🚀 Features

- **FastAPI REST API** - Modern, fast web framework with automatic API documentation
- **Redis Queue (RQ)** - Reliable background job processing with Redis
- **Docker Compose** - One-command deployment of the entire stack
- **Three Task Types** - CPU-intensive, I/O-intensive, and mathematical computations
- **Real-time Status Tracking** - Monitor task progress and retrieve results
- **Health Monitoring** - Built-in health checks and Redis connectivity status
- **Comprehensive Testing** - Complete API test suite with automated validation
- **Production Ready** - Containerized services with proper error handling

## 🏗️ Architecture

The project implements a **microservices architecture** with three main components:

```
                                                           
   FastAPI Web          Redis Server         RQ Worker     
   Application          (Message             (Background   
                         Broker)              Processor)   
   Port: 8000           Port: 6379                         
                                                           
```

### Workflow
1. **Client** sends POST request to enqueue a task
2. **FastAPI App** adds task to Redis queue and returns `task_id`
3. **RQ Worker** picks up task from queue and executes it in the background
4. **Client** polls `GET /tasks/{task_id}` to check status and retrieve results

## ⚡ Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) OpenWeatherMap API key for weather tasks

### 1. Clone and Start
```bash
git clone <repository-url>
cd fastapi-redis-queue-background-job-processing-demo

# Start all services
docker compose up -d
```

### 2. Test the API
```bash
# Check if services are running
curl http://localhost:8000/health

# Enqueue a prime number generation task
curl -X POST "http://localhost:8000/tasks/primes" \
  -H "Content-Type: application/json" \
  -d '{"start": 1, "end": 10000}'

# Response: {"task_id": "abc123...", "status": "enqueued", "message": "..."}
```

### 3. Check Task Status
```bash
# Replace {task_id} with actual ID from previous response
curl http://localhost:8000/tasks/{task_id}
```

### 4. Run Test Suite
```bash
# Validate all functionality with the comprehensive test suite
python test_api.py
```

### 5. View API Documentation
Open http://localhost:8000/docs in your browser for interactive API documentation.

## 📦 Installation

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd fastapi-redis-queue-background-job-processing-demo

# Optional: Set up environment variables
cp .env.example .env
# Edit .env and add your OPENWEATHER_API_KEY

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Option 2: Local Development

```bash
# Install dependencies
uv sync

# Start Redis server (separate terminal)
redis-server

# Start FastAPI application (separate terminal)
uvicorn main:app --reload

# Start RQ worker (separate terminal)
python worker.py
```

## 📖 Usage

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `GET` | `/health` | Health check with Redis connectivity |
| `POST` | `/tasks/primes` | Enqueue prime number generation |
| `POST` | `/tasks/fibonacci` | Enqueue Fibonacci calculation |
| `POST` | `/tasks/weather` | Enqueue weather data fetching |
| `GET` | `/tasks/{task_id}` | Get task status and results |

### Example Usage

#### 1. Prime Number Generation
```bash
# Enqueue task
curl -X POST "http://localhost:8000/tasks/primes" \
  -H "Content-Type: application/json" \
  -d '{"start": 1, "end": 50000}'

# Response
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "enqueued",
  "message": "Prime generation task enqueued for range 1-50000"
}
```

#### 2. Fibonacci Calculation
```bash
# Enqueue task (n=35 takes ~5-10 seconds)
curl -X POST "http://localhost:8000/tasks/fibonacci" \
  -H "Content-Type: application/json" \
  -d '{"n": 35}'
```

#### 3. Weather Data Fetching
```bash
# Enqueue task (requires OPENWEATHER_API_KEY)
curl -X POST "http://localhost:8000/tasks/weather"
```

#### 4. Check Task Status
```bash
# Check status - returns "pending", "in_progress", "completed", or "failed"
curl "http://localhost:8000/tasks/f47ac10b-58cc-4372-a567-0e02b2c3d479"

# Example completed response
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "completed",
  "result": {
    "primes": [2, 3, 5, 7, 11, ...],
    "count": 5133,
    "range": "1-50000",
    "execution_time": 4.23
  }
}
```

## 🔧 Background Tasks

### 1. Prime Number Generation
- **Function**: `find_primes_in_range(start, end)`
- **Purpose**: CPU-intensive task for demonstrating computational workloads
- **Performance**: 3-10 seconds for ranges like 1-100,000
- **Use Case**: Mathematical computations, data processing

### 2. Fibonacci Calculation
- **Function**: `calculate_fibonacci(n)`
- **Purpose**: Recursive computation that gets exponentially slower
- **Performance**: ~5-15 seconds for n=35-40
- **Use Case**: Algorithm benchmarking, performance testing

### 3. Weather Data Fetching
- **Function**: `fetch_weather_for_cities_sync()`
- **Purpose**: I/O-intensive task with external API calls
- **Performance**: 5-15 seconds for 15 cities (with rate limiting)
- **Use Case**: API integrations, data aggregation

## ⚙️ Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

### Environment Variables

```env
# OpenWeatherMap API (optional - for weather tasks)
OPENWEATHER_API_KEY=your_api_key_here

# Redis Configuration (Docker sets these automatically)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Getting an OpenWeatherMap API Key
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Add it to your `.env` file

## 🛠️ Development

### Project Structure
```
   main.py              # FastAPI application
   worker.py            # RQ worker process
   tasks.py             # Background task implementations
   demo.py              # Direct task testing (no queue)
   test_api.py          # Comprehensive API test suite
   docker-compose.yml   # Service orchestration
   Dockerfile           # Application container
   pyproject.toml       # Python dependencies
   .env.example         # Environment template
```

### Running Tests

#### Comprehensive API Test Suite
The project includes a comprehensive test script that validates all endpoints and functionality:

```bash
# Run the complete test suite
python test_api.py

# Run tests against a different URL
python test_api.py http://localhost:8000
```

The test script will:
- ✅ Test all API endpoints with real parameters
- ✅ Capture and validate task IDs for each submitted task
- ✅ Wait for task completion and verify results
- ✅ Test error handling with invalid inputs
- ✅ Provide colored output with detailed status reporting

#### Example Test Output
```
🚀 Starting FastAPI Redis Queue API Tests
Base URL: http://localhost:8000

ℹ️  Testing root endpoint (GET /)
✅ Root endpoint: Status code 200
✅ Root endpoint: Field 'message' = 'FastAPI Redis Queue Background Job Processing Demo'
✅ Root Endpoint: PASSED

ℹ️  Testing prime number task endpoint (POST /tasks/primes)
✅ Prime task creation: Status code 200
✅ Prime task creation: Field 'task_id' exists
ℹ️  Waiting for prime task 824c424a-b660-4978-8d1a-a0a4a1bb15ba to complete...
✅ Prime task completion: Field 'status' = 'completed'
✅ Prime task result count: Field 'count' = '168'
✅ Prime Task Endpoint: PASSED

📊 TEST SUMMARY
============================================================
Total Tests: 7
Passed: 7
Failed: 0
🎉 ALL TESTS PASSED!
```

#### Individual Task Testing
```bash
# Test individual tasks directly (bypasses queue)
python demo.py

# Test specific task functions
python -c "from tasks import find_primes_in_range; print(find_primes_in_range(1, 1000))"
```

### Development Commands
```bash
# Install dependencies
uv sync

# Format code
black . --line-length 88

# Type checking
mypy .

# Start development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Redis Queue Monitoring
```bash
# Connect to Redis container
docker exec -it fastapi-redis-demo-redis redis-cli

# Check queue length
LLEN rq:queue:default

# List all keys
KEYS *
```

### Logs
```bash
# View all service logs
docker compose logs -f

# View specific service logs
docker compose logs -f web
docker compose logs -f worker
docker compose logs -f redis
```

## 🔍 Troubleshooting

### Common Issues

**1. Redis Connection Failed**
```bash
# Check if Redis is running
docker compose ps

# Restart Redis service
docker compose restart redis
```

**2. Worker Not Processing Tasks**
```bash
# Check worker logs
docker compose logs worker

# Restart worker
docker compose restart worker
```

**3. Tasks Stuck in Queue**
```bash
# Clear Redis queue
docker exec -it fastapi-redis-demo-redis redis-cli FLUSHALL
```

**4. Weather Tasks Failing**
- Ensure `OPENWEATHER_API_KEY` is set in `.env`
- Check API key validity at OpenWeatherMap dashboard

### Performance Tips

- **CPU Tasks**: Adjust `start` and `end` ranges for prime generation
- **Fibonacci**: Values above n=40 can take very long (exponential growth)
- **Weather**: API has rate limits - tasks include built-in delays

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test them
4. Submit a pull request

## 📚 Learn More

This project demonstrates several important concepts:

- **Asynchronous Processing** - Offloading long-running tasks
- **Microservices Architecture** - Separating concerns into different services
- **Message Queues** - Using Redis for reliable task distribution
- **REST API Design** - Well-structured endpoints with proper status codes
- **Docker Orchestration** - Multi-container application deployment
- **Health Monitoring** - Service status and connectivity checks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you have questions or run into issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the API documentation at http://localhost:8000/docs
3. Open an issue on GitHub

---

**Happy coding!** 🎉