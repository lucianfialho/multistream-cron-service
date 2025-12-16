from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
import uvicorn
import os
import logging
from contextlib import asynccontextmanager

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management - startup and shutdown"""
    # Startup
    logger.info("🚀 Starting FastAPI application...")

    # Start APScheduler
    from jobs.scheduler import start_scheduler
    start_scheduler()

    yield

    # Shutdown
    logger.info("🛑 Shutting down FastAPI application...")
    from jobs.scheduler import shutdown_scheduler
    shutdown_scheduler()


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="HLTV Stats API for CS2 Events",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from routers import events, proxy
app.include_router(events.router, prefix="/api")
app.include_router(proxy.router, prefix="/api")

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

@app.get("/scheduler/status")
def scheduler_status():
    """Check scheduler status and list configured jobs"""
    from jobs.scheduler import scheduler

    jobs_info = []
    for job in scheduler.get_jobs():
        jobs_info.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger)
        })

    return {
        "running": scheduler.running,
        "jobs_count": len(jobs_info),
        "jobs": jobs_info
    }

@app.post("/trigger/sync-highlights")
def trigger_sync_highlights(eventId: str = "8042", eventSlug: str = "starladder-budapest-major-2025"):
    """Manually trigger event highlights sync"""
    from jobs.sync_highlights import sync_event_highlights
    try:
        sync_event_highlights(eventId, eventSlug)
        return {
            "status": "success",
            "message": f"Synced highlights for event {eventId}"
        }
    except Exception as e:
        logger.error(f"Error syncing highlights: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
