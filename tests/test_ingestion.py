from agents.ingestion_agent import IngestionAgent

# Initialize
agent = IngestionAgent(upload_dir="./uploads")

# Test with mock data
upload_data = {
    "xray_file": "./test_xray.png",  # Your test image
    "patient_info": {
        "age": 45,
        "gender": "M",
        "allergies": ["penicillin"]
    },
    "symptoms": "cough, fever",
    "spo2": 94
}

# Process
result = agent.process(upload_data)

# Check output
if result["status"] == "success":
    print(f"✅ X-ray saved: {result['xray_path']}")
    print(f"✅ Patient: {result['patient']['age']}y")
    print(f"✅ Notes: {result['notes']}")
else:
    print(f"❌ Error: {result['error']}")