#!/usr/bin/env python3
"""
Simple demonstration script for background task functions.
This script runs each function and prints the results and execution times.
"""

import os
import time
from dotenv import load_dotenv
from tasks import (
    find_primes_in_range,
    calculate_fibonacci,
    fetch_weather_for_cities_sync
)


def print_separator(title: str):
    """Print a nice separator with title."""
    print("\n" + "=" * 60)
    print(f" {title} ")
    print("=" * 60)


def demo_prime_numbers():
    """Demonstrate prime number generation."""
    print_separator("PRIME NUMBER GENERATION DEMO")
    
    test_cases = [
        (1, 1000),
        (1, 10000),
        (1, 50000),
    ]
    
    for start, end in test_cases:
        print(f"\nFinding primes in range {start}-{end}...")
        print("⏳ Processing...")
        
        start_time = time.time()
        result = find_primes_in_range(start, end)
        total_time = time.time() - start_time
        
        print(f"✅ Found {result['count']} prime numbers")
        print(f"⏰ Execution time: {result['execution_time']} seconds")
        print(f"📊 First 10 primes: {result['primes'][:10]}")
        if len(result['primes']) > 10:
            print(f"📊 Last 10 primes: {result['primes'][-10:]}")


def demo_fibonacci():
    """Demonstrate Fibonacci calculation."""
    print_separator("FIBONACCI CALCULATION DEMO")
    
    test_cases = [25, 30, 35, 38]
    
    for n in test_cases:
        print(f"\nCalculating Fibonacci number at position {n}...")
        print("⏳ Processing...")
        
        start_time = time.time()
        result = calculate_fibonacci(n)
        total_time = time.time() - start_time
        
        print(f"✅ Fibonacci({n}) = {result['fibonacci_number']}")
        print(f"⏰ Execution time: {result['execution_time']} seconds")


def demo_weather():
    """Demonstrate weather data fetching."""
    print_separator("WEATHER DATA FETCHING DEMO")
    
    # Check if API key is available
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print("❌ OpenWeatherMap API key not found!")
        print("💡 To run this demo:")
        print("   1. Sign up at https://openweathermap.org/api")
        print("   2. Get your free API key")
        print("   3. Set environment variable: export OPENWEATHER_API_KEY='your_key'")
        return
    
    print("🌍 Fetching weather data for major cities worldwide...")
    print("⏳ Processing (this may take 10-20 seconds)...")
    
    start_time = time.time()
    result = fetch_weather_for_cities_sync()
    total_time = time.time() - start_time
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"✅ Successfully fetched weather for {result['successful_requests']} cities")
    print(f"⏰ Execution time: {result['execution_time']} seconds")
    
    if result['failed_requests']:
        print(f"⚠️  Failed requests: {len(result['failed_requests'])}")
    
    print("\n🌡️  Weather Summary:")
    print("-" * 50)
    
    for city_data in result['cities_data'][:10]:  # Show first 10 cities
        temp = city_data['temperature']
        desc = city_data['description'].title()
        city = city_data['city']
        country = city_data['country']
        print(f"{city}, {country}: {temp}°C - {desc}")
    
    if len(result['cities_data']) > 10:
        print(f"... and {len(result['cities_data']) - 10} more cities")


def main():
    # Load environment variables from .env file
    load_dotenv()

    """Run all demonstrations."""
    print("🚀 Background Tasks Demonstration")
    print("This script demonstrates three types of background tasks:")
    print("1. CPU-intensive: Prime number generation")
    print("2. CPU-intensive: Fibonacci calculation")
    print("3. I/O-intensive: Weather API calls")
    
    try:
        # Demo 1: Prime Numbers
        demo_prime_numbers()
        
        # Demo 2: Fibonacci
        demo_fibonacci()
        
        # Demo 3: Weather (if API key available)
        demo_weather()
        
        print_separator("DEMONSTRATION COMPLETE")
        print("✅ All demonstrations completed successfully!")
        print("\n💡 Key Observations:")
        print("   • Tasks take several seconds to complete")
        print("   • In a web application, these would block the UI")
        print("   • Background processing with Redis Queue solves this!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        print("Please check your dependencies and environment setup.")


if __name__ == "__main__":
    main()