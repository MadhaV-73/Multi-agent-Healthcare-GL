from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

app = FastAPI(
    title="Multi-Agent Healthcare API",
    description="API for healthcare multi-agent system with patient analysis and document processing",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import integrated routes with agent pipeline
from api.routes_integrated import router
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Healthcare API - Integrated with Agent Pipeline",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "patient_analysis": "/api/v1/patient/analysis",
            "xray_analysis": "/api/v1/xray/analyze (NEW - Full Pipeline Integration)",
            "file_upload": "/api/v1/upload/documents",
            "health_check": "/api/v1/health",
            "test_agents": "/api/v1/test"
        }
    }

@app.get("/get")
def test_get():
    return {"message":"Hello world","success":True}

# POST -> Upload the image / pdf or both together 

if __name__ == "__main__":
    print("🚀 Starting Multi-Agent Healthcare API...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/api/v1/health")
    print("🧪 Test Endpoint: http://localhost:8000/api/v1/test")
    print("✅ All 6 agents initialized")
    uvicorn.run(app, host="0.0.0.0", port=8000)