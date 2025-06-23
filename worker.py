#!/usr/bin/env python3
"""
Redis Queue Worker for background task processing.
This script creates and runs an RQ worker to process jobs from the Redis queue.
"""

import os
import sys
import redis
from rq import Worker, Queue
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import task functions so they're available to the worker
from tasks import (
    find_primes_in_range,
    calculate_fibonacci,
    fetch_weather_for_cities_sync
)

def main():
    """Start the RQ worker."""
    # Redis connection configuration
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    
    print(f"Connecting to Redis at {redis_host}:{redis_port}")
    
    try:
        # Create Redis connection (no decode_responses for RQ binary data)
        redis_conn = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=False,
            health_check_interval=30
        )
        
        # Test the connection
        redis_conn.ping()
        print("✅ Redis connection successful")
        
        # Create queue
        queue = Queue(connection=redis_conn)
        
        print(f"📋 Queue length: {len(queue)}")
        print("🚀 Starting RQ worker...")
        print("📝 Available tasks:")
        print("   - find_primes_in_range")
        print("   - calculate_fibonacci") 
        print("   - fetch_weather_for_cities_sync")
        print("\n⏳ Waiting for jobs... (Press Ctrl+C to exit)")
        
        # Start the worker
        worker = Worker([queue], connection=redis_conn)
        worker.work(with_scheduler=True)
            
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        print("Make sure Redis server is running and accessible.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Worker stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Worker error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()