from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.core.config import settings
from app.core.logging import logger
from app.db.session import SessionLocal
from app.models.hospital import Hospital
from app.utils.rate_limiter import RateLimitMiddleware
from app.ai.model_service import AISeverityService

# Import routers
from app.api.auth import router as auth_router
from app.api.accident import router as accident_router
from app.api.sos import router as sos_router
from app.api.location import router as location_router
from app.api.ai import router as ai_router
from app.api.hospital import router as hospital_router
from app.api.contacts import router as contacts_router
from app.api.authority import router as authority_router
from app.api.volunteers import router as volunteers_router
from app.api.ambulances import router as ambulances_router
from app.api.first_aid import router as first_aid_router
from app.api.gov import router as gov_router


# Async Startup/Shutdown lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Initializing Golden Minute AI backend...")

    # Load model (and train if missing)
    AISeverityService.get_model()

    # Auto-create tables for SQLite fallback
    from app.db.session import engine
    if "sqlite" in str(engine.url):
        from app.db.base import Base
        logger.info("SQLite database detected. Auto-creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Seed mock hospitals database entries if table is empty
    async with SessionLocal() as session:
        try:
            result = await session.execute(select(Hospital))
            count = len(result.scalars().all())
            if count == 0:
                logger.info("Seeding database with default emergency trauma hospitals...")
                mock_hospitals = [
                    Hospital(
                        name="Apex Trauma Center (Level 1)",
                        latitude=12.971598,
                        longitude=77.594566,
                        trauma_level=1,
                        available_beds=10,
                        ventilators=6,
                    ),
                    Hospital(
                        name="City General Hospital (Level 2)",
                        latitude=12.982598,
                        longitude=77.601566,
                        trauma_level=2,
                        available_beds=15,
                        ventilators=2,
                    ),
                    Hospital(
                        name="St. Jude Clinic (Level 3)",
                        latitude=12.961598,
                        longitude=77.584566,
                        trauma_level=3,
                        available_beds=8,
                        ventilators=1,
                    ),
                    Hospital(
                        name="Metro SuperSpecialty Hospital",
                        latitude=12.991598,
                        longitude=77.624566,
                        trauma_level=1,
                        available_beds=3,
                        ventilators=10,
                    ),
                ]
                session.add_all(mock_hospitals)
                await session.commit()
                logger.info("Database seeding successfully completed.")
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await session.rollback()

    yield
    # Shutdown logic
    logger.info("Shutting down Golden Minute AI backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Rate Limiter middleware (120 requests/minute default)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)

# Wire Routes
app.include_router(auth_router, prefix=settings.API_STR)
app.include_router(accident_router, prefix=settings.API_STR)
app.include_router(sos_router, prefix=settings.API_STR)
app.include_router(location_router, prefix=settings.API_STR)
app.include_router(ai_router, prefix=settings.API_STR)
app.include_router(hospital_router, prefix=settings.API_STR)
app.include_router(contacts_router, prefix=settings.API_STR)
app.include_router(authority_router, prefix=settings.API_STR)
app.include_router(volunteers_router, prefix=settings.API_STR)
app.include_router(ambulances_router, prefix=settings.API_STR)
app.include_router(first_aid_router, prefix=settings.API_STR)
app.include_router(gov_router, prefix=settings.API_STR)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "api_docs": "/docs",
    }
