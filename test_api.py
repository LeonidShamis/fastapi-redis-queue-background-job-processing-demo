#!/usr/bin/env python3
"""
Comprehensive test script for FastAPI Redis Queue Background Job Processing Demo.
Tests all API endpoints with various scenarios and validates responses.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def log(self, message: str, color: str = Colors.CYAN):
        print(f"{color}{message}{Colors.END}")

    def log_success(self, message: str):
        self.log(f"✅ {message}", Colors.GREEN)

    def log_error(self, message: str):
        self.log(f"❌ {message}", Colors.RED)

    def log_info(self, message: str):
        self.log(f"ℹ️  {message}", Colors.BLUE)

    def assert_status_code(self, response: requests.Response, expected: int, test_name: str):
        """Assert HTTP status code matches expected value."""
        if response.status_code == expected:
            self.log_success(f"{test_name}: Status code {response.status_code}")
            return True
        else:
            self.log_error(f"{test_name}: Expected status {expected}, got {response.status_code}")
            return False

    def assert_json_field(self, data: Dict[str, Any], field: str, expected_value: Any, test_name: str):
        """Assert JSON field matches expected value."""
        if field in data and data[field] == expected_value:
            self.log_success(f"{test_name}: Field '{field}' = '{expected_value}'")
            return True
        else:
            actual_value = data.get(field, "MISSING")
            self.log_error(f"{test_name}: Field '{field}' expected '{expected_value}', got '{actual_value}'")
            return False

    def assert_json_field_exists(self, data: Dict[str, Any], field: str, test_name: str):
        """Assert JSON field exists."""
        if field in data:
            self.log_success(f"{test_name}: Field '{field}' exists")
            return True
        else:
            self.log_error(f"{test_name}: Field '{field}' missing")
            return False

    def wait_for_task_completion(self, task_id: str, timeout: int = TIMEOUT) -> Optional[Dict[str, Any]]:
        """Wait for a task to complete and return the result."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/tasks/{task_id}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') in ['completed', 'failed']:
                        return data
                time.sleep(1)
            except Exception as e:
                self.log_error(f"Error checking task status: {e}")
                return None
        
        self.log_error(f"Task {task_id} did not complete within {timeout} seconds")
        return None

    def test_root_endpoint(self):
        """Test GET / endpoint."""
        self.log_info("Testing root endpoint (GET /)")
        
        try:
            response = requests.get(f"{self.base_url}/")
            success = True
            
            # Check status code
            success &= self.assert_status_code(response, 200, "Root endpoint")
            
            # Check response structure
            data = response.json()
            success &= self.assert_json_field(data, "message", "FastAPI Redis Queue Background Job Processing Demo", "Root endpoint")
            success &= self.assert_json_field_exists(data, "docs", "Root endpoint")
            success &= self.assert_json_field_exists(data, "health", "Root endpoint")
            success &= self.assert_json_field_exists(data, "endpoints", "Root endpoint")
            
            # Check endpoints structure
            if "endpoints" in data:
                endpoints = data["endpoints"]
                success &= self.assert_json_field(endpoints, "enqueue_primes", "POST /tasks/primes", "Root endpoint")
                success &= self.assert_json_field(endpoints, "enqueue_fibonacci", "POST /tasks/fibonacci", "Root endpoint")
                success &= self.assert_json_field(endpoints, "enqueue_weather", "POST /tasks/weather", "Root endpoint")
                success &= self.assert_json_field(endpoints, "check_task_status", "GET /tasks/{task_id}", "Root endpoint")
            
            self.record_test("Root Endpoint", success)
            
        except Exception as e:
            self.log_error(f"Root endpoint test failed: {e}")
            self.record_test("Root Endpoint", False)

    def test_health_endpoint(self):
        """Test GET /health endpoint."""
        self.log_info("Testing health endpoint (GET /health)")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            success = True
            
            # Check status code
            success &= self.assert_status_code(response, 200, "Health endpoint")
            
            # Check response structure
            data = response.json()
            success &= self.assert_json_field(data, "status", "healthy", "Health endpoint")
            success &= self.assert_json_field(data, "redis_connection", "connected", "Health endpoint")
            success &= self.assert_json_field_exists(data, "queue_length", "Health endpoint")
            
            self.record_test("Health Endpoint", success)
            
        except Exception as e:
            self.log_error(f"Health endpoint test failed: {e}")
            self.record_test("Health Endpoint", False)

    def test_prime_task_endpoint(self):
        """Test POST /tasks/primes endpoint."""
        self.log_info("Testing prime number task endpoint (POST /tasks/primes)")
        
        try:
            # Test parameters used in manual testing
            payload = {"start": 1, "end": 1000}
            response = requests.post(
                f"{self.base_url}/tasks/primes",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            success = True
            
            # Check status code
            success &= self.assert_status_code(response, 200, "Prime task creation")
            
            # Check response structure
            data = response.json()
            success &= self.assert_json_field_exists(data, "task_id", "Prime task creation")
            success &= self.assert_json_field(data, "status", "enqueued", "Prime task creation")
            success &= self.assert_json_field(data, "message", "Prime generation task enqueued for range 1-1000", "Prime task creation")
            
            if success and "task_id" in data:
                task_id = data["task_id"]
                self.log_info(f"Waiting for prime task {task_id} to complete...")
                
                # Wait for task completion
                task_result = self.wait_for_task_completion(task_id)
                if task_result:
                    success &= self.assert_json_field(task_result, "status", "completed", "Prime task completion")
                    success &= self.assert_json_field_exists(task_result, "result", "Prime task completion")
                    
                    if "result" in task_result:
                        result = task_result["result"]
                        success &= self.assert_json_field_exists(result, "primes", "Prime task result")
                        success &= self.assert_json_field_exists(result, "count", "Prime task result")
                        success &= self.assert_json_field(result, "range", "1-1000", "Prime task result")
                        success &= self.assert_json_field_exists(result, "execution_time", "Prime task result")
                        
                        # Check that we got 168 primes (correct count for 1-1000)
                        if "count" in result:
                            success &= self.assert_json_field(result, "count", 168, "Prime task result count")
                else:
                    success = False
            
            self.record_test("Prime Task Endpoint", success)
            
        except Exception as e:
            self.log_error(f"Prime task endpoint test failed: {e}")
            self.record_test("Prime Task Endpoint", False)

    def test_fibonacci_task_endpoint(self):
        """Test POST /tasks/fibonacci endpoint."""
        self.log_info("Testing Fibonacci task endpoint (POST /tasks/fibonacci)")
        
        try:
            # Test parameters used in manual testing
            payload = {"n": 30}
            response = requests.post(
                f"{self.base_url}/tasks/fibonacci",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            success = True
            
            # Check status code
            success &= self.assert_status_code(response, 200, "Fibonacci task creation")
            
            # Check response structure
            data = response.json()
            success &= self.assert_json_field_exists(data, "task_id", "Fibonacci task creation")
            success &= self.assert_json_field(data, "status", "enqueued", "Fibonacci task creation")
            success &= self.assert_json_field(data, "message", "Fibonacci calculation task enqueued for n=30", "Fibonacci task creation")
            
            if success and "task_id" in data:
                task_id = data["task_id"]
                self.log_info(f"Waiting for Fibonacci task {task_id} to complete...")
                
                # Wait for task completion
                task_result = self.wait_for_task_completion(task_id)
                if task_result:
                    success &= self.assert_json_field(task_result, "status", "completed", "Fibonacci task completion")
                    success &= self.assert_json_field_exists(task_result, "result", "Fibonacci task completion")
                    
                    if "result" in task_result:
                        result = task_result["result"]
                        success &= self.assert_json_field_exists(result, "fibonacci_number", "Fibonacci task result")
                        success &= self.assert_json_field(result, "position", 30, "Fibonacci task result")
                        success &= self.assert_json_field_exists(result, "execution_time", "Fibonacci task result")
                        
                        # Check that we got the correct Fibonacci number for n=30 (832040)
                        if "fibonacci_number" in result:
                            success &= self.assert_json_field(result, "fibonacci_number", 832040, "Fibonacci task result number")
                else:
                    success = False
            
            self.record_test("Fibonacci Task Endpoint", success)
            
        except Exception as e:
            self.log_error(f"Fibonacci task endpoint test failed: {e}")
            self.record_test("Fibonacci Task Endpoint", False)

    def test_weather_task_endpoint(self):
        """Test POST /tasks/weather endpoint."""
        self.log_info("Testing weather task endpoint (POST /tasks/weather)")
        
        try:
            response = requests.post(
                f"{self.base_url}/tasks/weather",
                headers={"Content-Type": "application/json"}
            )
            
            success = True
            
            # Check status code
            success &= self.assert_status_code(response, 200, "Weather task creation")
            
            # Check response structure
            data = response.json()
            success &= self.assert_json_field_exists(data, "task_id", "Weather task creation")
            success &= self.assert_json_field(data, "status", "enqueued", "Weather task creation")
            success &= self.assert_json_field(data, "message", "Weather data fetching task enqueued", "Weather task creation")
            
            if success and "task_id" in data:
                task_id = data["task_id"]
                self.log_info(f"Waiting for weather task {task_id} to complete...")
                
                # Wait for task completion
                task_result = self.wait_for_task_completion(task_id)
                if task_result:
                    success &= self.assert_json_field(task_result, "status", "completed", "Weather task completion")
                    success &= self.assert_json_field_exists(task_result, "result", "Weather task completion")
                    
                    if "result" in task_result:
                        result = task_result["result"]
                        success &= self.assert_json_field_exists(result, "cities_data", "Weather task result")
                        success &= self.assert_json_field_exists(result, "successful_requests", "Weather task result")
                        success &= self.assert_json_field_exists(result, "failed_requests", "Weather task result")
                        success &= self.assert_json_field_exists(result, "total_cities_attempted", "Weather task result")
                        success &= self.assert_json_field_exists(result, "execution_time", "Weather task result")
                        
                        # Check that we attempted 15 cities
                        if "total_cities_attempted" in result:
                            success &= self.assert_json_field(result, "total_cities_attempted", 15, "Weather task cities count")
                else:
                    success = False
            
            self.record_test("Weather Task Endpoint", success)
            
        except Exception as e:
            self.log_error(f"Weather task endpoint test failed: {e}")
            self.record_test("Weather Task Endpoint", False)

    def test_task_status_endpoint(self):
        """Test GET /tasks/{task_id} endpoint."""
        self.log_info("Testing task status endpoint (GET /tasks/{task_id})")
        
        try:
            # Test with non-existent task ID
            response = requests.get(f"{self.base_url}/tasks/nonexistent-task-id")
            success = True
            
            # Should return 404 for non-existent task
            success &= self.assert_status_code(response, 404, "Task status (non-existent)")
            
            data = response.json()
            success &= self.assert_json_field(data, "detail", "Task not found", "Task status (non-existent)")
            
            self.record_test("Task Status Endpoint", success)
            
        except Exception as e:
            self.log_error(f"Task status endpoint test failed: {e}")
            self.record_test("Task Status Endpoint", False)

    def test_error_cases(self):
        """Test various error cases."""
        self.log_info("Testing error cases")
        
        success = True
        
        try:
            # Test prime task with invalid data
            response = requests.post(
                f"{self.base_url}/tasks/primes",
                json={"start": "invalid", "end": 100},
                headers={"Content-Type": "application/json"}
            )
            success &= self.assert_status_code(response, 422, "Prime task (invalid data)")
            
            # Test Fibonacci task with missing data
            response = requests.post(
                f"{self.base_url}/tasks/fibonacci",
                json={},
                headers={"Content-Type": "application/json"}
            )
            success &= self.assert_status_code(response, 422, "Fibonacci task (missing data)")
            
            self.record_test("Error Cases", success)
            
        except Exception as e:
            self.log_error(f"Error cases test failed: {e}")
            self.record_test("Error Cases", False)

    def record_test(self, test_name: str, passed: bool):
        """Record test result."""
        if passed:
            self.tests_passed += 1
            self.log_success(f"{test_name}: PASSED")
        else:
            self.tests_failed += 1
            self.log_error(f"{test_name}: FAILED")
        
        self.test_results.append({"name": test_name, "passed": passed})

    def run_all_tests(self):
        """Run all tests."""
        self.log(f"{Colors.BOLD}🚀 Starting FastAPI Redis Queue API Tests{Colors.END}")
        self.log(f"{Colors.BOLD}Base URL: {self.base_url}{Colors.END}")
        print()
        
        # Run all test methods
        self.test_root_endpoint()
        print()
        
        self.test_health_endpoint()
        print()
        
        self.test_prime_task_endpoint()
        print()
        
        self.test_fibonacci_task_endpoint()
        print()
        
        self.test_weather_task_endpoint()
        print()
        
        self.test_task_status_endpoint()
        print()
        
        self.test_error_cases()
        print()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        total_tests = self.tests_passed + self.tests_failed
        
        print("=" * 60)
        self.log(f"{Colors.BOLD}📊 TEST SUMMARY{Colors.END}")
        print("=" * 60)
        
        self.log(f"Total Tests: {total_tests}", Colors.CYAN)
        self.log(f"Passed: {self.tests_passed}", Colors.GREEN)
        self.log(f"Failed: {self.tests_failed}", Colors.RED)
        
        if self.tests_failed == 0:
            self.log(f"{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.END}", Colors.GREEN)
        else:
            self.log(f"{Colors.BOLD}⚠️  {self.tests_failed} TEST(S) FAILED{Colors.END}", Colors.RED)
        
        print()
        self.log("Test Results:", Colors.CYAN)
        for result in self.test_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            color = Colors.GREEN if result["passed"] else Colors.RED
            self.log(f"  {result['name']}: {status}", color)
        
        print("=" * 60)
        
        return self.tests_failed == 0

def main():
    """Main function."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
    
    tester = APITester(base_url)
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Tests failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()