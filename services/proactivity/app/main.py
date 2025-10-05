from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from scheduler import ProactivityScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    logger.info("Starting Jarvis Proactivity Engine...")
    
    scheduler = ProactivityScheduler()
    scheduler.start()
    logger.info("Proactivity scheduler started")
    
    yield
    
    logger.info("Shutting down Jarvis Proactivity Engine...")
    if scheduler:
        scheduler.shutdown()

app = FastAPI(
    title="Jarvis Proactivity Engine",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def root():
    return {
        "service": "Jarvis Proactivity Engine",
        "status": "running",
        "description": "Proaktive Erinnerungen und Benachrichtigungen"
    }

@app.get("/health")
def health_check():
    status = "healthy"
    scheduler_status = "running" if scheduler and scheduler.is_running() else "stopped"
    
    return {
        "status": status,
        "scheduler": scheduler_status
    }

@app.get("/v1/status")
def get_status():
    if not scheduler:
        return {"error": "Scheduler not initialized"}
    
    return {
        "scheduler_running": scheduler.is_running(),
        "active_time_windows": scheduler.get_active_time_windows(),
        "notification_count_today": scheduler.get_notification_count()
    }
