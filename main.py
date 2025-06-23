from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
from rq import Queue
from rq.job import Job
import os
from typing import Dict, Any, Optional
from tasks import find_primes_in_range, calculate_fibonacci, fetch_weather_for_cities_sync

app = FastAPI(
    title="FastAPI Redis Queue Background Job Processing Demo",
    description="Demo application showing background job processing with FastAPI and Redis Queue",
    version="1.0.0"
)

# Redis connection
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))

# Use single Redis connection without decode_responses for RQ compatibility
redis_conn = redis.Redis(host=redis_host, port=redis_port, decode_responses=False)
queue = Queue(connection=redis_conn)

# Request models
class PrimeRequest(BaseModel):
    start: int
    end: int

class FibonacciRequest(BaseModel):
    n: int

# Response models
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint that tests Redis connectivity."""
    try:
        # Test Redis connection
        redis_conn.ping()
        return {
            "status": "healthy",
            "redis_connection": "connected",
            "queue_length": len(queue)
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "redis_connection": "failed",
                "error": str(e)
            }
        )

@app.post("/tasks/primes", response_model=TaskResponse)
async def enqueue_prime_task(request: PrimeRequest):
    """Enqueue a prime number generation task."""
    try:
        job = queue.enqueue(find_primes_in_range, request.start, request.end)
        return TaskResponse(
            task_id=job.id,
            status="enqueued",
            message=f"Prime generation task enqueued for range {request.start}-{request.end}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue task: {str(e)}")

@app.post("/tasks/fibonacci", response_model=TaskResponse)
async def enqueue_fibonacci_task(request: FibonacciRequest):
    """Enqueue a Fibonacci calculation task."""
    try:
        job = queue.enqueue(calculate_fibonacci, request.n)
        return TaskResponse(
            task_id=job.id,
            status="enqueued",
            message=f"Fibonacci calculation task enqueued for n={request.n}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue task: {str(e)}")

@app.post("/tasks/weather", response_model=TaskResponse)
async def enqueue_weather_task():
    """Enqueue a weather data fetching task."""
    try:
        job = queue.enqueue(fetch_weather_for_cities_sync)
        return TaskResponse(
            task_id=job.id,
            status="enqueued",
            message="Weather data fetching task enqueued"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue task: {str(e)}")

@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the status and result of a specific task."""
    try:
        # Use RQ's Job class to properly handle serialization
        job = Job.fetch(task_id, connection=redis_conn)
        
        if job.is_finished:
            return TaskStatusResponse(
                task_id=task_id,
                status="completed",
                result=job.result
            )
        elif job.is_failed:
            return TaskStatusResponse(
                task_id=task_id,
                status="failed",
                error=str(job.exc_info) if job.exc_info else "Unknown error"
            )
        elif job.is_started:
            return TaskStatusResponse(
                task_id=task_id,
                status="in_progress"
            )
        elif job.is_queued:
            return TaskStatusResponse(
                task_id=task_id,
                status="pending"
            )
        else:
            return TaskStatusResponse(
                task_id=task_id,
                status="unknown"
            )
            
    except Exception as e:
        # If job doesn't exist or other error
        if "No such job" in str(e):
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "FastAPI Redis Queue Background Job Processing Demo",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "enqueue_primes": "POST /tasks/primes",
            "enqueue_fibonacci": "POST /tasks/fibonacci", 
            "enqueue_weather": "POST /tasks/weather",
            "check_task_status": "GET /tasks/{task_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
