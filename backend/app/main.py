from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.api.v1.endpoints import complaints
from app.database import engine, Base

# Lifespan context manager handles startup and shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield  # The application runs here
    
    # Shutdown logic: Close database connections
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Include Routers
app.include_router(
    complaints.router, 
    prefix=f"{settings.API_V1_STR}/complaints", 
    tags=["Complaints"]
)

@app.get("/")
async def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)