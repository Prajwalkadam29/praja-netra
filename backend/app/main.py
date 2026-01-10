from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
# Import the new routers
from app.api.v1.endpoints import complaints, admin, auth, official, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# 1. Citizen Routes
app.include_router(
    complaints.router,
    prefix=f"{settings.API_V1_STR}/complaints",
    tags=["Complaints"]
)

# 2. Official/Department Routes
app.include_router(
    official.router,
    prefix=f"{settings.API_V1_STR}/official",
    tags=["Official Management"]
)

# 3. Analytics & Dashboard Data (Used by Admin/Official)
app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_STR}/analytics",
    tags=["Analytics"]
)

# 4. Auth & Admin
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

@app.get("/")
async def health_check():
    return {"status": "online", "project": settings.PROJECT_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)