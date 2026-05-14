"""
Voice pair mappings for Pace's multi-voice dialogue system.

Each category maps to a "show" — two ElevenLabs voices with a defined personality.
Replace PLACEHOLDER_A / PLACEHOLDER_B with real ElevenLabs voice IDs before going live.
"""

# ---------------------------------------------------------------------------
# Show definitions
# ---------------------------------------------------------------------------

_SHOWS: dict[str, dict] = {
    "SPORTS_BROS": {
        "show": "SPORTS_BROS",
        "voice_a": "YVyp28LAMQfmx8iIH88U",
        "voice_b": "lKf2tqVafNW1nVb7CgwC",
        "personality": (
            "Sports radio energy. Voice A is hype and excitable — loves the drama, "
            "talks fast, jumps on big plays. Voice B is dry and analytical with "
            "sarcastic humor — brings the stats, deflates the hype just enough. "
            "Think Pat McAfee + a stats nerd who can't help being right."
        ),
    },
    "TECH_HEADS": {
        "show": "TECH_HEADS",
        "voice_a": "tMvyQtpCVQ0DkixuYm6J",
        "voice_b": "8DzKSPdgEQPaK5vKG0Rs",
        "personality": (
            "Voice A is genuinely excited about new tech — loves explaining, gets "
            "nerdy about details, optimistic by default. Voice B is skeptical and "
            "practical — always asking what it actually costs, who it's really for, "
            "and where the catch is. Think Hard Fork podcast."
        ),
    },
    "CRIME_FILES": {
        "show": "CRIME_FILES",
        "voice_a": "jJvIIsFGSxzXLCRjq5Xf",
        "voice_b": "dAlhI9qAHVIjXuVppzhW",
        "personality": (
            "Voice A is a deliberate storyteller — atmospheric, measured, lets the "
            "facts land. Voice B reacts with theories, dark observations, and "
            "occasional dark humor. Both take the subject seriously. "
            "Think Crime Junkie energy."
        ),
    },
    "CURIOUS_ONES": {
        "show": "CURIOUS_ONES",
        "voice_a": "rhKGiHCLeAC5KPBEZiUq",
        "voice_b": "DYkrAHD8iwork3YSUBbs",
        "personality": (
            "Voice A is curious and slightly awestruck — leads with wonder, loves "
            "the weird implications of discoveries. Voice B grounds everything in "
            "real-world consequences — connects abstract science to what it means "
            "for actual people. Think Radiolab energy."
        ),
    },
    "DAILY_BRIEFING": {
        "show": "DAILY_BRIEFING",
        "voice_a": "IUKR8VQRbh1g1fP708FJ",
        "voice_b": "TTY70JqFvDxeExufZ1za",
        "personality": (
            "Voice A reports with conversational sharpness — direct, informed, no "
            "fluff. Voice B asks what this means for normal people — skeptical of "
            "spin, pulls things back to ground level. Less hype, more substance."
        ),
    },
    "POP_OFF": {
        "show": "POP_OFF",
        "voice_a": "yl2ZDV1MzN4HbQJbMihG",
        "voice_b": "UgBBYS2sOqTuMpoF3BR0",
        "personality": (
            "Voice A is the pop culture insider — has strong opinions, knows the "
            "context, picks sides. Voice B is the casual fan who reacts like the "
            "average viewer — surprised by deep cuts, has hot takes of their own."
        ),
    },
    "REAL_TALK": {
        "show": "REAL_TALK",
        "voice_a": "Anr9GtYh2VRXxiPplzxM",
        "voice_b": "UalXHhfqFg6JugnheN0j",
        "personality": (
            "Voice A is the cool friend casually sharing wellness and lifestyle "
            "stuff — no preachy energy, just genuinely useful. Voice B is the "
            "reasonable skeptic — asks if it actually works, checks the trade-offs."
        ),
    },
}

# ---------------------------------------------------------------------------
# Category → show mapping
# ---------------------------------------------------------------------------

_CATEGORY_TO_SHOW: dict[str, str] = {
    # SPORTS_BROS
    "nba": "SPORTS_BROS",
    "nfl": "SPORTS_BROS",
    "soccer": "SPORTS_BROS",
    "mlb": "SPORTS_BROS",
    # TECH_HEADS
    "ai": "TECH_HEADS",
    "tech": "TECH_HEADS",
    "startups": "TECH_HEADS",
    "gadgets": "TECH_HEADS",
    "gaming": "TECH_HEADS",
    # CRIME_FILES
    "true_crime": "CRIME_FILES",
    "history": "CRIME_FILES",
    # CURIOUS_ONES
    "space": "CURIOUS_ONES",
    "science": "CURIOUS_ONES",
    "climate": "CURIOUS_ONES",
    "psychology": "CURIOUS_ONES",
    # DAILY_BRIEFING
    "us_politics": "DAILY_BRIEFING",
    "world_news": "DAILY_BRIEFING",
    "business": "DAILY_BRIEFING",
    "markets": "DAILY_BRIEFING",
    # POP_OFF
    "movies": "POP_OFF",
    "tv": "POP_OFF",
    "music": "POP_OFF",
    # REAL_TALK
    "health": "REAL_TALK",
    "food": "REAL_TALK",
    "travel": "REAL_TALK",
}

_DEFAULT_SHOW = "DAILY_BRIEFING"


def get_voice_pair(category: str) -> dict:
    """
    Return the voice pair config dict for *category*.

    Falls back to DAILY_BRIEFING if the category has no mapping.
    The returned dict has keys: show, voice_a, voice_b, personality.
    """
    show_key = _CATEGORY_TO_SHOW.get(category.lower(), _DEFAULT_SHOW)
    return _SHOWS[show_key]
