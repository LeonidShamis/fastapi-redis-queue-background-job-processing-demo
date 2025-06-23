# examples of tasks that may take some time and therefore should be run in the background

import time
import math
import asyncio
import aiohttp
from typing import List, Dict, Any
import os


def find_primes_in_range(start: int, end: int) -> Dict[str, Any]:
    """
    Find all prime numbers in a given range.
    Takes 3-10 seconds for ranges like 1-100000.
    
    Args:
        start: Starting number of the range
        end: Ending number of the range
        
    Returns:
        Dict containing primes list, count, and execution time
    """
    start_time = time.time()
    
    def is_prime(n):
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    primes = []
    for num in range(start, end + 1):
        if is_prime(num):
            primes.append(num)
    
    execution_time = time.time() - start_time
    
    return {
        "primes": primes,
        "count": len(primes),
        "range": f"{start}-{end}",
        "execution_time": round(execution_time, 2)
    }


def calculate_fibonacci(n: int) -> Dict[str, Any]:
    """
    Calculate the nth Fibonacci number using recursive approach.
    Gets slow around n=35-40, taking several seconds.
    
    Args:
        n: Position in Fibonacci sequence
        
    Returns:
        Dict containing the Fibonacci number and execution time
    """
    start_time = time.time()
    
    def fib_recursive(num):
        if num <= 1:
            return num
        return fib_recursive(num - 1) + fib_recursive(num - 2)
    
    # For demonstration purposes, we'll use the slow recursive approach
    # for n > 30 to show the background processing benefit
    if n <= 30:
        # Use efficient approach for smaller numbers
        def fib_iterative(num):
            if num <= 1:
                return num
            a, b = 0, 1
            for _ in range(2, num + 1):
                a, b = b, a + b
            return b
        
        result = fib_iterative(n)
    else:
        # Use slow recursive approach to demonstrate background processing
        result = fib_recursive(n)
    
    execution_time = time.time() - start_time
    
    return {
        "fibonacci_number": result,
        "position": n,
        "execution_time": round(execution_time, 2)
    }


async def fetch_weather_for_cities() -> Dict[str, Any]:
    """
    Fetch weather data for multiple cities using OpenWeatherMap API.
    Takes 5-15 seconds depending on number of cities and API response times.
    
    Returns:
        Dict containing weather data for all cities and execution time
    """
    start_time = time.time()
    
    # Get API key from environment variable
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        return {
            "error": "OpenWeatherMap API key not found. Set OPENWEATHER_API_KEY environment variable.",
            "cities_data": [],
            "execution_time": 0
        }
    
    # List of cities to fetch weather for
    cities = [
        "London,UK",
        "New York,US",
        "Tokyo,JP",
        "Paris,FR",
        "Sydney,AU",
        "Mumbai,IN",
        "São Paulo,BR",
        "Cairo,EG",
        "Moscow,RU",
        "Cape Town,ZA",
        "Toronto,CA",
        "Berlin,DE",
        "Bangkok,TH",
        "Mexico City,MX",
        "Buenos Aires,AR"
    ]
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    cities_data = []
    failed_cities = []
    
    async with aiohttp.ClientSession() as session:
        for city in cities:
            try:
                params = {
                    'q': city,
                    'appid': api_key,
                    'units': 'metric'  # Use Celsius
                }
                
                async with session.get(base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        city_weather = {
                            "city": data['name'],
                            "country": data['sys']['country'],
                            "temperature": data['main']['temp'],
                            "feels_like": data['main']['feels_like'],
                            "humidity": data['main']['humidity'],
                            "description": data['weather'][0]['description'],
                            "wind_speed": data['wind']['speed']
                        }
                        cities_data.append(city_weather)
                    else:
                        failed_cities.append(f"{city} (HTTP {response.status})")
                
                # Add small delay to avoid hitting API rate limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed_cities.append(f"{city} (Error: {str(e)})")
    
    execution_time = time.time() - start_time
    
    return {
        "cities_data": cities_data,
        "successful_requests": len(cities_data),
        "failed_requests": failed_cities,
        "total_cities_attempted": len(cities),
        "execution_time": round(execution_time, 2)
    }


# Wrapper function for Redis Queue (since RQ doesn't handle async functions directly)
def fetch_weather_for_cities_sync() -> Dict[str, Any]:
    """
    Synchronous wrapper for the async weather fetching function.
    This is needed because Redis Queue doesn't handle async functions directly.
    """
    return asyncio.run(fetch_weather_for_cities())
