from fastapi import FastAPI

app = FastAPI(
    title="Japanese Learning API Test",
    description="Basic test version",
    version="1.0.0",
)

@app.get("/")
async def root():
    return {"message": "Hello from Japanese Learning API", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "test-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)