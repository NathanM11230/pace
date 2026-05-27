"""
One-time backfill: append the brand chime to all existing snippet audio files.

Skips snippets where has_whoosh is already True.
Adds the has_whoosh column to the DB if it doesn't exist yet.

Run once:
    python append_whoosh_to_existing.py
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
logger = logging.getLogger("backfill")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent
CHIME_PATH   = PROJECT_ROOT / "audio_files" / "whoosh.mp3"

if not CHIME_PATH.exists():
    logger.error("Chime file not found at '%s'. Run generate_whoosh.py first.", CHIME_PATH)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Wire pydub ffmpeg (same as audio_generator.py)
# ---------------------------------------------------------------------------
from pydub import AudioSegment
try:
    import imageio_ffmpeg
    _exe = imageio_ffmpeg.get_ffmpeg_exe()
    AudioSegment.converter = _exe
    AudioSegment.ffmpeg = _exe
except ImportError:
    pass

chime = AudioSegment.from_file(str(CHIME_PATH), format="mp3", codec="mp3")
logger.info("Chime loaded: %d ms", len(chime))

# ---------------------------------------------------------------------------
# DB setup — add has_whoosh column if missing
# ---------------------------------------------------------------------------
from sqlalchemy import create_engine, text
from app.config import settings
from app.models import Base, Snippet
from sqlalchemy.orm import Session

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

# Ensure column exists (SQLite supports ADD COLUMN)
with engine.connect() as conn:
    cols = [row[1] for row in conn.execute(text("PRAGMA table_info(snippets)"))]
    if "has_whoosh" not in cols:
        conn.execute(text("ALTER TABLE snippets ADD COLUMN has_whoosh BOOLEAN NOT NULL DEFAULT 0"))
        conn.commit()
        logger.info("Added has_whoosh column to snippets table.")

# ---------------------------------------------------------------------------
# Backfill
# ---------------------------------------------------------------------------
with Session(engine) as db:
    snippets = (
        db.query(Snippet)
        .filter(Snippet.has_whoosh == False, Snippet.audio_file.isnot(None))  # noqa: E712
        .all()
    )
    logger.info("Found %d snippet(s) to backfill.", len(snippets))

    ok = skip = fail = 0

    for snippet in snippets:
        audio_path = Path(snippet.audio_file)
        if not audio_path.exists():
            logger.warning("  [%d] File not found: %s — skipping.", snippet.id, audio_path)
            skip += 1
            continue

        try:
            original = AudioSegment.from_file(str(audio_path), format="mp3", codec="mp3")
            combined = original + chime
            combined.export(str(audio_path), format="mp3")
            snippet.has_whoosh = True
            db.commit()
            logger.info("  [%d] %-55s +%d ms → %d ms total",
                        snippet.id, audio_path.name[:55],
                        len(chime), len(combined))
            ok += 1
        except Exception as exc:
            logger.error("  [%d] Failed: %s", snippet.id, exc)
            fail += 1

    logger.info("Done. %d updated, %d skipped, %d failed.", ok, skip, fail)
