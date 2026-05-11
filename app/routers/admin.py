import logging
import threading
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.schemas import GenerationStatus
from app.services.content_generator import generate_daily_content, generation_status
from app.services.news_fetcher import CATEGORIES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Track the background job ID so clients can correlate requests
_current_job_id: str | None = None


def _run_generation_in_background(job_id: str) -> None:
    """Run the full content generation pipeline with its own DB session."""
    logger.info("Background generation started (job_id=%s).", job_id)
    try:
        with SessionLocal() as db:
            generate_daily_content(db)
    except Exception as exc:
        logger.exception("Background generation failed (job_id=%s): %s", job_id, exc)
        generation_status.update(
            {
                "status": "failed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    logger.info("Background generation finished (job_id=%s).", job_id)


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
def trigger_generation():
    """
    Kick off content generation in a background thread.
    Returns 202 Accepted immediately with a job ID.
    If a generation is already running, returns 409 Conflict.
    """
    global _current_job_id

    if generation_status.get("status") == "running":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "A generation job is already running.",
                "job_id": _current_job_id,
            },
        )

    job_id = str(uuid.uuid4())
    _current_job_id = job_id

    thread = threading.Thread(
        target=_run_generation_in_background,
        args=(job_id,),
        daemon=True,
        name=f"pace-gen-{job_id[:8]}",
    )
    thread.start()

    logger.info("Dispatched generation job_id=%s.", job_id)
    return {"status": "accepted", "job_id": job_id, "message": "Content generation started."}


@router.get("/status", response_model=GenerationStatus)
def get_generation_status():
    """Return the status of the most recent (or current) generation run."""
    return GenerationStatus(
        status=generation_status.get("status", "idle"),
        snippets_generated=generation_status.get("snippets_generated", 0),
        errors=generation_status.get("errors", 0),
        started_at=generation_status.get("started_at"),
        completed_at=generation_status.get("completed_at"),
    )


@router.get("/categories")
def list_categories():
    """Return the available content categories and their associated queries."""
    return {
        "categories": list(CATEGORIES.keys()),
        "details": CATEGORIES,
    }
