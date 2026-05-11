import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Snippet, User, UserSnippetInteraction
from app.schemas import FeedResponse, InteractionCreate, SnippetResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feed", tags=["feed"])


def _get_user_or_404(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )
    return user


@router.get("/{user_id}", response_model=FeedResponse)
def get_feed(user_id: int, db: Session = Depends(get_db)):
    """
    Return a personalised feed of up to 20 active snippets for the user.

    Logic:
    - Fetch user's interest categories.
    - Find snippet IDs the user has already interacted with today (any action).
    - Return active snippets in those categories, excluding already-seen ones,
      ordered newest-first.
    - If the user has no interests set, return recent snippets across all categories.
    """
    user = _get_user_or_404(user_id, db)

    # Start of today in UTC
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Snippet IDs the user has already interacted with today
    interacted_today = (
        db.query(UserSnippetInteraction.snippet_id)
        .filter(
            UserSnippetInteraction.user_id == user_id,
            UserSnippetInteraction.timestamp >= today_start,
        )
        .all()
    )
    excluded_ids = {row.snippet_id for row in interacted_today}

    base_query = db.query(Snippet).filter(Snippet.is_active == True)  # noqa: E712

    interests: list[str] = user.interests or []
    if interests:
        base_query = base_query.filter(Snippet.category.in_(interests))

    if excluded_ids:
        base_query = base_query.filter(Snippet.id.notin_(excluded_ids))

    snippets = base_query.order_by(Snippet.created_at.desc()).limit(20).all()

    return FeedResponse(
        snippets=[SnippetResponse.model_validate(s) for s in snippets],
        total=len(snippets),
    )


@router.post("/{user_id}/interact", status_code=status.HTTP_201_CREATED)
def record_interaction(
    user_id: int,
    payload: InteractionCreate,
    db: Session = Depends(get_db),
):
    """Record a user interaction (played, completed, skipped) with a snippet."""
    _get_user_or_404(user_id, db)

    snippet = (
        db.query(Snippet)
        .filter(Snippet.id == payload.snippet_id, Snippet.is_active == True)  # noqa: E712
        .first()
    )
    if not snippet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snippet {payload.snippet_id} not found.",
        )

    interaction = UserSnippetInteraction(
        user_id=user_id,
        snippet_id=payload.snippet_id,
        action=payload.action,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    logger.info(
        "Interaction recorded: user=%d snippet=%d action=%s",
        user_id,
        payload.snippet_id,
        payload.action,
    )
    return {"id": interaction.id, "status": "recorded"}
