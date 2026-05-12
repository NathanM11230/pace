import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Snippet

logger = logging.getLogger(__name__)

_RETENTION_HOURS = 48


def cleanup_old_snippets(db: Session) -> dict:
    """
    Soft-deletes snippets older than 48 hours and removes their audio files from disk.

    Returns a summary dict with counts of deactivated snippets and deleted audio files.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=_RETENTION_HOURS)

    old_snippets = (
        db.query(Snippet)
        .filter(Snippet.is_active == True, Snippet.created_at < cutoff)
        .all()
    )

    if not old_snippets:
        logger.info("Cleanup: no snippets older than %dh found.", _RETENTION_HOURS)
        return {"deactivated": 0, "audio_files_deleted": 0}

    audio_deleted = 0
    for snippet in old_snippets:
        snippet.is_active = False
        if snippet.audio_file:
            audio_path = Path(snippet.audio_file)
            if audio_path.exists():
                try:
                    audio_path.unlink()
                    audio_deleted += 1
                except OSError as exc:
                    logger.warning(
                        "Could not delete audio file '%s': %s", audio_path, exc
                    )

    db.commit()

    logger.info(
        "Cleanup complete: deactivated %d snippets, deleted %d audio files.",
        len(old_snippets),
        audio_deleted,
    )
    return {"deactivated": len(old_snippets), "audio_files_deleted": audio_deleted}
