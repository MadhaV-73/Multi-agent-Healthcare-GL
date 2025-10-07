import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
        "message": "Multi-Agent Healthcare API - Deployed on Render",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)