from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/get")
def test_get():
    return {"message":"Hello world","success":True}

# POST -> Upload the image / pdf or both together 




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)