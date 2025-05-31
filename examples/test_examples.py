import requests
import time
import subprocess
import sys
import os
from concurrent.futures import ThreadPoolExecutor

def test_endpoint(url, user_agent=None):
    """Test an endpoint with optional user agent"""
    headers = {}
    if user_agent:
        headers['User-Agent'] = user_agent
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}, Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_rate_limiting(url, num_requests=70):
    """Test rate limiting by making multiple requests"""
    print(f"\nTesting rate limiting for {url}")
    success_count = 0
    
    for i in range(num_requests):
        if test_endpoint(url):
            success_count += 1
        time.sleep(0.1)  # Small delay between requests
    
    print(f"Success rate: {success_count}/{num_requests}")
    return success_count

def test_user_agent_blocking(url):
    """Test user agent blocking"""
    print(f"\nTesting user agent blocking for {url}")
    
    # Test with blocked user agent
    blocked_agents = ["curl/7.64.1", "wget/1.20.3", "Scrapy/2.5.0"]
    for agent in blocked_agents:
        print(f"\nTesting with blocked agent: {agent}")
        test_endpoint(url, user_agent=agent)
    
    # Test with allowed user agent
    print("\nTesting with allowed agent: Mozilla/5.0")
    test_endpoint(url, user_agent="Mozilla/5.0")

def run_tests(base_url):
    """Run all tests for a given base URL"""
    print(f"\nTesting endpoints at {base_url}")
    
    # Test root endpoint
    print("\nTesting root endpoint")
    test_endpoint(f"{base_url}/")
    
    # Test sensitive endpoint with rate limiting
    test_rate_limiting(f"{base_url}/api/sensitive", num_requests=15)
    
    # Test user agent blocking
    test_user_agent_blocking(f"{base_url}/api/blocked")

def main():
    # Start FastAPI server
    print("Starting FastAPI server...")
    fastapi_process = subprocess.Popen(
        [sys.executable, "examples/fastapi_example.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for FastAPI server to start
    time.sleep(2)
    
    # Run FastAPI tests
    run_tests("http://localhost:8000")
    
    # Stop FastAPI server
    fastapi_process.terminate()
    
    # Start Flask server
    print("\nStarting Flask server...")
    flask_process = subprocess.Popen(
        [sys.executable, "examples/flask_example.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for Flask server to start
    time.sleep(2)
    
    # Run Flask tests
    run_tests("http://localhost:5000")
    
    # Stop Flask server
    flask_process.terminate()

if __name__ == "__main__":
    main() 