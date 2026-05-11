import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Snippet
from app.schemas import SnippetResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/snippets", tags=["snippets"])


@router.get("", response_model=list[SnippetResponse])
def list_snippets(
    category: str | None = Query(default=None, description="Filter by category"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List active snippets, optionally filtered by category.
    Supports pagination via limit/offset.
    """
    query = db.query(Snippet).filter(Snippet.is_active == True)  # noqa: E712
    if category:
        query = query.filter(Snippet.category == category)
    snippets = (
        query.order_by(Snippet.created_at.desc()).offset(offset).limit(limit).all()
    )
    return snippets


@router.get("/{snippet_id}", response_model=SnippetResponse)
def get_snippet(snippet_id: int, db: Session = Depends(get_db)):
    """Retrieve a single snippet by ID."""
    snippet = (
        db.query(Snippet)
        .filter(Snippet.id == snippet_id, Snippet.is_active == True)  # noqa: E712
        .first()
    )
    if not snippet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet {snippet_id} not found.",
        )
    return snippet


@router.get("/{snippet_id}/audio")
def get_snippet_audio(snippet_id: int, db: Session = Depends(get_db)):
    """
    Stream the MP3 audio file for a snippet.
    Returns 404 if the snippet has no audio yet.
    """
    snippet = (
        db.query(Snippet)
        .filter(Snippet.id == snippet_id, Snippet.is_active == True)  # noqa: E712
        .first()
    )
    if not snippet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet {snippet_id} not found.",
        )

    if not snippet.audio_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No audio available for snippet {snippet_id}.",
        )

    audio_path = Path(snippet.audio_file)
    if not audio_path.exists():
        logger.warning(
            "Audio file listed in DB but missing on disk: %s", snippet.audio_file
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file is missing from disk.",
        )

    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=audio_path.name,
    )
