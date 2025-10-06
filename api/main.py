from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Multi-Agent Healthcare API",
    description="API for healthcare multi-agent system with patient analysis and document processing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from api.routes import router
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Multi-Agent Healthcare API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "patient_analysis": "/api/v1/patient/analysis",
            "file_upload": "/api/v1/upload/documents",
            "health_check": "/api/v1/health"
        }
    }

@app.get("/get")
def test_get():
    return {"message":"Hello world","success":True}

# POST -> Upload the image / pdf or both together 

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)