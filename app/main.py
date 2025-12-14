from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
import uvicorn
import os

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="HLTV Stats API for CS2 Events"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic endpoints only
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": settings.api_title,
        "version": settings.api_version
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
