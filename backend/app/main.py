from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import jobs, monitoring
from app.scheduler import scheduler
from app.database import engine
from app.models import Base

app = FastAPI(title="XTrack API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app"
    ],  # React dev servers + Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler on application startup"""
    print("[STARTUP] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[STARTUP] ✅ Database tables created")
    
    print("[STARTUP] Starting job scheduler...")
    scheduler.start()
    print("[STARTUP] ✅ Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the job scheduler on application shutdown"""
    print("[SHUTDOWN] Stopping job scheduler...")
    scheduler.stop()
    print("[SHUTDOWN] ✅ Application shutdown complete")

@app.get("/")
async def root():
    return {"message": "XTrack API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

