"""
Quick test script to verify backend API connection
"""
import requests
import json

API_BASE_URL = "https://multi-agent-healthcare-gl-1.onrender.com"

print("=" * 60)
print("Testing Backend API Connection")
print("=" * 60)
print(f"\nBackend URL: {API_BASE_URL}\n")

# Test 1: Root endpoint
print("1️⃣ Testing Root Endpoint...")
try:
    response = requests.get(f"{API_BASE_URL}/", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        print("   ✅ Root endpoint working!")
    else:
        print(f"   ❌ Unexpected status code: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 2: Health endpoint
print("2️⃣ Testing Health Check Endpoint...")
try:
    response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        print("   ✅ Health check endpoint working!")
    else:
        print(f"   ❌ Unexpected status code: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 3: API Docs
print("3️⃣ Testing API Documentation...")
try:
    response = requests.get(f"{API_BASE_URL}/docs", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ API docs accessible at: {API_BASE_URL}/docs")
    else:
        print(f"   ❌ Unexpected status code: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("=" * 60)
print("Test Complete!")
print("=" * 60)
print(f"\n📚 View full API documentation at: {API_BASE_URL}/docs")
print(f"🔗 Your backend is live at: {API_BASE_URL}\n")
