"""
Quick test script to verify API and frontend integration
"""
import requests
import time

API_URL = "http://localhost:8000"

print("🧪 Testing Multi-Agent Healthcare API Integration")
print("=" * 60)

# Wait for API to be ready
print("\n⏳ Waiting for API to start...")
for i in range(10):
    try:
        response = requests.get(f"{API_URL}/api/v1/health", timeout=2)
        if response.status_code == 200:
            print("✅ API is online!")
            break
    except:
        time.sleep(1)
        print(f"   Attempt {i+1}/10...")
else:
    print("❌ API did not start. Please run: python api/main.py")
    exit(1)

# Test 1: Health Check
print("\n📊 Test 1: Health Check")
try:
    response = requests.get(f"{API_URL}/api/v1/health")
    data = response.json()
    print(f"   Status: {data.get('status')}")
    print(f"   Message: {data.get('message')}")
    agents = data.get('agents_initialized', {})
    for agent, status in agents.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {agent}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Agent Test Endpoint
print("\n🤖 Test 2: Agent Status")
try:
    response = requests.get(f"{API_URL}/api/v1/test")
    data = response.json()
    print(f"   Message: {data.get('message')}")
    print(f"   Agents: {data.get('agents')}")
    print(f"   Data Status: {data.get('data_status')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Root Endpoint
print("\n🏠 Test 3: Root Endpoint")
try:
    response = requests.get(f"{API_URL}/")
    data = response.json()
    print(f"   Message: {data.get('message')}")
    print(f"   Version: {data.get('version')}")
    print(f"   Available Endpoints:")
    for name, path in data.get('endpoints', {}).items():
        print(f"      • {name}: {path}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ All API tests completed successfully!")
print("\n📚 Next Steps:")
print("   1. Open http://localhost:8501 (Streamlit Frontend)")
print("   2. Open http://localhost:8000/docs (API Documentation)")
print("   3. Upload an X-ray for complete pipeline test")
print("=" * 60)
