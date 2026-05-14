"""
Run the full generation pipeline for a single hardcoded article.
Bypasses NewsAPI — use this when the quota is exhausted.

Output: dialogue script + audio saved to DB and audio_files/.
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(name)s: %(message)s",
    stream=sys.stdout,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("anthropic").setLevel(logging.WARNING)

ARTICLE = {
    "title": "OpenAI Launches GPT-5 With Native Voice and Real-Time Web Search Built In",
    "source": "The Verge",
    "description": (
        "OpenAI announced GPT-5 today, a multimodal model that natively integrates "
        "voice conversation, real-time web search, and image generation into a single "
        "unified system. The model is available immediately to ChatGPT Plus subscribers "
        "and will roll out to free users over the next two weeks. OpenAI claims GPT-5 "
        "scores 20 points higher than GPT-4o on standard reasoning benchmarks and can "
        "hold 10-minute voice conversations with near-zero latency."
    ),
    "content": (
        "OpenAI today unveiled GPT-5, its most capable model to date, featuring native "
        "voice interaction, real-time internet search, and integrated image generation "
        "without switching between tools. The company says GPT-5 is available now in "
        "ChatGPT for Plus subscribers, with a free-tier rollout planned over the coming weeks.\n\n"
        "The new model scores 87% on the MMLU benchmark — up from GPT-4o's 67% — and "
        "achieves 72% on ARC-AGI, a test designed to resist AI pattern-matching. OpenAI "
        "CEO Sam Altman described GPT-5 as 'the first model that genuinely surprised us "
        "during evals,' without elaborating.\n\n"
        "Voice mode latency has been reduced to under 200 milliseconds on average, making "
        "conversations feel closer to phone-call quality. The built-in search pulls live "
        "results from the web and cites sources inline. Image generation uses a new "
        "diffusion architecture co-developed with the DALL-E team.\n\n"
        "Pricing remains $20/month for Plus. An API tier for GPT-5 will be announced "
        "separately next week."
    ),
    "url": "https://example.com/gpt5-launch",
    "publishedAt": "2026-05-14T10:00:00Z",
}

CATEGORY = "ai"


def main():
    from app.config import settings
    from app.database import SessionLocal
    from app.models import Snippet
    from app.services.audio_generator import generate_audio
    from app.services.content_generator import _safe_filename
    from app.services.summarizer import summarize_article
    from app.services.voice_pairs import get_voice_pair

    db = SessionLocal()
    audio_dir = Path(settings.audio_files_dir)

    try:
        voice_pair = get_voice_pair(CATEGORY)
        print(f"\nShow: {voice_pair['show']}")
        print(f"Article: {ARTICLE['title']}\n")

        # 1. Generate dialogue script
        print("[1/3] Generating dialogue script...")
        script = summarize_article(ARTICLE, CATEGORY)
        if not script:
            print("ERROR: Script generation failed.")
            sys.exit(1)

        print("\n--- SCRIPT ---")
        print(script)
        print("--------------\n")

        # 2. Save to DB
        print("[2/3] Saving to database...")
        snippet = Snippet(
            category=CATEGORY,
            title=ARTICLE["title"],
            source=ARTICLE["source"],
            article_url=ARTICLE["url"],
            published_at=ARTICLE["publishedAt"],
            script=script,
            word_count=len(script.split()),
            audio_file=None,
            is_active=True,
        )
        db.add(snippet)
        db.commit()
        db.refresh(snippet)
        print(f"Snippet saved with ID: {snippet.id}")

        # 3. Generate audio
        print("[3/3] Generating audio...")
        safe_title = _safe_filename(ARTICLE["title"])
        audio_filename = f"{CATEGORY}_{snippet.id}_{safe_title}.mp3"
        audio_path = generate_audio(script, CATEGORY, audio_filename, audio_dir)

        if audio_path:
            snippet.audio_file = audio_path
            db.commit()
            print(f"\nDone. Audio saved to: {audio_path}")
        else:
            print("\nWARNING: Audio generation failed — snippet saved to DB without audio.")

    except Exception as exc:
        print(f"ERROR: {exc}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
