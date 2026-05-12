import logging
from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import SessionLocal, init_db
from app.routers import admin, feed, snippets, users
from app.services.cleanup import cleanup_old_snippets
from app.services.content_generator import generate_daily_content

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scheduled job wrapper — uses its own DB session
# ---------------------------------------------------------------------------

def run_scheduled_generation() -> None:
    """Called by APScheduler. Creates a fresh DB session for the generation run."""
    logger.info("Scheduled daily content generation starting.")
    try:
        with SessionLocal() as db:
            result = generate_daily_content(db)
        logger.info("Scheduled generation complete: %s", result)
    except Exception as exc:
        logger.exception("Scheduled generation failed: %s", exc)


def run_scheduled_cleanup() -> None:
    """Called by APScheduler. Removes snippets older than 48 hours."""
    logger.info("Scheduled snippet cleanup starting.")
    try:
        with SessionLocal() as db:
            result = cleanup_old_snippets(db)
        logger.info("Scheduled cleanup complete: %s", result)
    except Exception as exc:
        logger.exception("Scheduled cleanup failed: %s", exc)


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- Startup ----
    logger.info("Pace API starting up.")

    # Create DB tables
    init_db()
    logger.info("Database initialised.")

    # Create audio output directory
    audio_dir = Path(settings.audio_files_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Audio directory ready at '%s'.", audio_dir.resolve())

    # Start background scheduler
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_scheduled_generation,
        "cron",
        hour=settings.scheduler_hour,
        minute=settings.scheduler_minute,
        id="daily_content_generation",
        replace_existing=True,
    )
    scheduler.add_job(
        run_scheduled_cleanup,
        "cron",
        hour=settings.scheduler_hour,
        minute=settings.scheduler_minute + 5,
        id="daily_snippet_cleanup",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started. Daily generation at %02d:%02d UTC.",
        settings.scheduler_hour,
        settings.scheduler_minute,
    )

    yield

    # ---- Shutdown ----
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down. Pace API stopping.")


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Pace API",
    description="Backend API for the Pace running-companion audio snippet app.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "The requested resource was not found."},
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed.", "errors": str(exc)},
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(users.router)
app.include_router(snippets.router)
app.include_router(feed.router)
app.include_router(admin.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok", "service": "pace-api"}
