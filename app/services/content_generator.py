import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Snippet
from app.services.audio_generator import generate_audio
from app.services.news_fetcher import CATEGORIES, fetch_articles
from app.services.summarizer import summarize_article
from app.services.voice_pairs import get_voice_pair

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared generation status — read by the admin router
# ---------------------------------------------------------------------------

generation_status: dict = {
    "status": "idle",
    "snippets_generated": 0,
    "errors": 0,
    "started_at": None,
    "completed_at": None,
}


_STOP_WORDS = {
    "the", "and", "for", "with", "this", "that", "from", "have", "will",
    "about", "after", "also", "been", "into", "more", "news", "says",
    "than", "their", "they", "what", "when", "where", "which", "who",
    "your", "amid", "over", "amid", "amid",
}


def _key_terms(title: str) -> frozenset[str]:
    """Extract significant lowercase words (>4 chars, not stop words) from a title."""
    words = re.sub(r"[^\w\s]", " ", title.lower()).split()
    return frozenset(w for w in words if len(w) > 4 and w not in _STOP_WORDS)


def _is_duplicate_event(title: str, seen_term_sets: list[frozenset]) -> bool:
    """Return True if this title shares 3+ key terms with any already-seen title."""
    terms = _key_terms(title)
    if not terms:
        return False
    return any(len(terms & seen) >= 3 for seen in seen_term_sets)


def _safe_filename(text: str, max_len: int = 40) -> str:
    """Convert arbitrary text to a filesystem-safe ASCII slug."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_-]+", "_", slug).strip("_")
    return slug[:max_len]


def generate_daily_content(db: Session) -> dict:
    """
    Full pipeline: fetch articles -> summarize with Claude -> generate audio -> save to DB.

    Updates the module-level *generation_status* dict throughout execution and
    returns a summary dict when complete.
    """
    global generation_status

    started_at = datetime.now(timezone.utc).isoformat()
    generation_status.update(
        {
            "status": "running",
            "snippets_generated": 0,
            "errors": 0,
            "started_at": started_at,
            "completed_at": None,
        }
    )

    snippets_generated = 0
    errors = 0
    audio_dir = Path(settings.audio_files_dir)

    # Seed seen_term_sets from existing DB snippets so cross-run dedup works
    existing_titles = [row[0] for row in db.query(Snippet.title).all()]
    seen_term_sets: list[frozenset] = [_key_terms(t) for t in existing_titles]
    logger.info("Loaded %d existing snippet titles for dedup.", len(seen_term_sets))

    try:
        # TESTING MODE: Only generate 25 snippets total
        max_total_snippets = 25

        for category, queries in CATEGORIES.items():
            for query in queries:
                # Stop if we've reached our test limit
                if snippets_generated >= max_total_snippets:
                    logger.info(f"Reached test limit of {max_total_snippets} snippets. Stopping.")
                    break

                articles = fetch_articles(category, query, max_articles=2)
                for article in articles:
                    try:
                        title = article.get("title", "").strip()
                        if not title:
                            logger.warning("Skipping article with no title.")
                            errors += 1
                            continue

                        # De-duplicate: skip exact title matches already in DB
                        existing = (
                            db.query(Snippet)
                            .filter(Snippet.title == title)
                            .first()
                        )
                        if existing:
                            logger.info("Skipping duplicate article: '%s'", title[:60])
                            continue

                        # De-duplicate: skip same-event articles seen this run
                        if _is_duplicate_event(title, seen_term_sets):
                            logger.info("Skipping same-event duplicate: '%s'", title[:60])
                            continue

                        # 1. Summarize
                        show_name = get_voice_pair(category)["show"]
                        logger.info(
                            "Generating snippet for show '%s' (category='%s'): '%s'",
                            show_name,
                            category,
                            title[:60],
                        )
                        script = summarize_article(article, category)
                        if not script:
                            logger.error(
                                "Skipping article — dialogue script was None "
                                "(API failure or quality filter): '%s'",
                                title[:60],
                            )
                            errors += 1
                            continue

                        word_count = len(script.split())

                        # 2. Persist to DB first so we have an ID for the filename
                        snippet = Snippet(
                            category=category,
                            title=title,
                            source=article.get("source", "Unknown"),
                            article_url=article.get("url", ""),
                            published_at=article.get("publishedAt", ""),
                            script=script,
                            word_count=word_count,
                            audio_file=None,
                            is_active=True,
                        )
                        db.add(snippet)
                        db.commit()
                        db.refresh(snippet)

                        # 3. Generate audio
                        safe_title = _safe_filename(title)
                        audio_filename = f"{category}_{snippet.id}_{safe_title}.mp3"
                        audio_path = generate_audio(script, category, audio_filename, audio_dir)

                        if audio_path:
                            snippet.audio_file = audio_path
                            db.commit()

                        snippets_generated += 1
                        seen_term_sets.append(_key_terms(title))
                        generation_status["snippets_generated"] = snippets_generated
                        logger.info(
                            "Snippet #%d created for category='%s': '%s'",
                            snippet.id,
                            category,
                            title[:60],
                        )

                        # Rate-limit Claude calls — 1 second between requests
                        time.sleep(1)

                    except Exception as exc:
                        logger.exception(
                            "Error processing article '%s': %s",
                            article.get("title", "unknown")[:60],
                            exc,
                        )
                        errors += 1
                        db.rollback()
            if snippets_generated >= max_total_snippets:
                break

    except Exception as exc:
        logger.exception("Fatal error during content generation: %s", exc)
        errors += 1

    completed_at = datetime.now(timezone.utc).isoformat()
    result = {
        "status": "completed",
        "snippets_generated": snippets_generated,
        "errors": errors,
        "started_at": started_at,
        "completed_at": completed_at,
    }
    generation_status.update(result)
    logger.info(
        "Content generation finished: %d snippets, %d errors.", snippets_generated, errors
    )
    return result
