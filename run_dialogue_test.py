"""
Dialogue pipeline test — runs a single end-to-end snippet without touching the database.

Usage:
    python run_dialogue_test.py

Output:
    - Prints the raw dialogue script from Claude
    - Prints each parsed line with timing metadata
    - Generates multi-voice audio → test_audio/dialogue_test.mp3
"""

import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging — show INFO+ to stdout so timing decisions are visible
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(name)s: %(message)s",
    stream=sys.stdout,
)
# Quiet noisy third-party loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("anthropic").setLevel(logging.WARNING)

logger = logging.getLogger("dialogue_test")

# ---------------------------------------------------------------------------
# Hardcoded test article — fake tech story
# ---------------------------------------------------------------------------
TEST_ARTICLE = {
    "title": "Google DeepMind releases Gemini Code Ultra, claims it outperforms human senior engineers on real codebases",
    "source": "The Verge",
    "description": (
        "Google DeepMind today announced Gemini Code Ultra, a coding-focused model "
        "that the company claims achieves a 91% score on SWE-bench Verified — "
        "a benchmark that tests AI on real GitHub issues from popular open-source "
        "projects. The model can autonomously navigate large codebases, write and "
        "run tests, and submit pull requests without human intervention. Google says "
        "Code Ultra will be available to enterprise customers at $200 per developer "
        "per month, with a waitlist opening today."
    ),
    "content": (
        "Google DeepMind has released Gemini Code Ultra, a new AI model purpose-built "
        "for software engineering tasks. In internal evals and the public SWE-bench "
        "Verified benchmark, Code Ultra solved 91% of real-world GitHub issues — "
        "surpassing both Claude 3.7 Sonnet (76%) and OpenAI's o3 (71.7%). "
        "\n\n"
        "The model operates in a full agentic loop: given a GitHub issue, it reads "
        "the relevant files, writes a fix, runs the test suite, iterates on failures, "
        "and opens a pull request. In a demo, Google showed it resolving a three-year-old "
        "bug in the Django ORM in under four minutes. "
        "\n\n"
        "Pricing starts at $200 per developer per month for enterprise, with API access "
        "priced at $15 per million input tokens and $60 per million output tokens — "
        "significantly higher than standard Gemini 1.5 Pro. Google says the premium "
        "reflects Code Ultra's ability to replace 'a meaningful portion' of junior "
        "engineering work. Engineers and developers have reacted with a mix of "
        "excitement and anxiety on social media, with the phrase 'entry-level dev jobs' "
        "trending on X within hours of the announcement."
    ),
    "url": "https://example.com/gemini-code-ultra",
    "publishedAt": "2026-05-12T09:00:00Z",
}

TEST_CATEGORY = "ai"
OUTPUT_DIR = Path("test_audio")
OUTPUT_FILE = "dialogue_test.mp3"


def main() -> None:
    logger.info("=" * 60)
    logger.info("DIALOGUE PIPELINE TEST")
    logger.info("Category: %s | Article: %s", TEST_CATEGORY, TEST_ARTICLE["title"][:60])
    logger.info("=" * 60)

    # ---- Step 1: Generate dialogue script ----------------------------------
    logger.info("\n[STEP 1] Generating dialogue script via Claude...")
    from app.services.summarizer import summarize_article
    from app.services.voice_pairs import get_voice_pair

    voice_pair = get_voice_pair(TEST_CATEGORY)
    logger.info("Show: %s", voice_pair["show"])
    logger.info("Personality: %s", voice_pair["personality"])

    script = summarize_article(TEST_ARTICLE, TEST_CATEGORY)
    if not script:
        logger.error("Script generation failed or was rejected by quality filter. Exiting.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("RAW DIALOGUE SCRIPT")
    print("=" * 60)
    print(script)
    print("=" * 60)

    # ---- Step 2: Parse dialogue -------------------------------------------
    logger.info("\n[STEP 2] Parsing dialogue...")
    from app.services.audio_generator import parse_dialogue

    lines = parse_dialogue(script)
    if not lines:
        logger.error("No lines parsed from script. Check format.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"PARSED DIALOGUE ({len(lines)} lines)")
    print("=" * 60)
    for i, line in enumerate(lines):
        interrupt_flag = " [INTERRUPTION]" if line["has_interruption"] else ""
        print(
            f"  [{i:02d}] Voice {line['voice']} | ends_with={line['ends_with']!r:5s}"
            f"{interrupt_flag}"
        )
        print(f"        text: {line['text']!r}")
    print("=" * 60)

    # ---- Step 3: Generate multi-voice audio --------------------------------
    logger.info("\n[STEP 3] Generating multi-voice audio...")
    logger.info(
        "Voice A ID: %s | Voice B ID: %s",
        voice_pair["voice_a"],
        voice_pair["voice_b"],
    )

    if "PLACEHOLDER" in voice_pair["voice_a"]:
        logger.warning(
            "Voice IDs are still placeholders. ElevenLabs calls will fail.\n"
            "Replace PLACEHOLDER_A / PLACEHOLDER_B in app/services/voice_pairs.py "
            "with real ElevenLabs voice IDs before running audio generation."
        )
        logger.info("Skipping audio generation — replace voice IDs first.")
        print("\nTest complete (no audio generated — voice IDs are placeholders).")
        return

    from app.services.audio_generator import generate_audio

    audio_path = generate_audio(script, TEST_CATEGORY, OUTPUT_FILE, OUTPUT_DIR)
    if audio_path:
        print(f"\nAudio saved to: {audio_path}")
    else:
        logger.error("Audio generation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
