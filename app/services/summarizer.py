import logging
import random
import re
from collections import deque

import anthropic

from app.config import settings
from app.services.voice_pairs import get_voice_pair

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Energy options — one is randomly injected per snippet
# ---------------------------------------------------------------------------
_ENERGY_OPTIONS = [
    "curious", "skeptical", "amused", "surprised",
    "measured", "playful", "contemplative", "energized",
]

# ---------------------------------------------------------------------------
# Opening-pattern tracking — last 5 patterns, used to nudge variety
# ---------------------------------------------------------------------------
_recent_opening_patterns: deque[str] = deque(maxlen=5)


def _detect_opening_pattern(script: str) -> str:
    """Classify the opening style of a generated script into one of five buckets."""
    for raw in script.splitlines():
        raw = raw.strip()
        match = re.match(r"^[AB]:\s*(.+)$", raw)
        if not match:
            continue
        text = match.group(1).strip()
        if not text:
            continue

        # Question
        if text.endswith("?"):
            return "question"

        words = text.split()
        first = words[0].lower().rstrip(",") if words else ""

        # Reaction opener
        reaction_starters = {
            "oh", "yeah", "right", "huh", "look", "so", "okay", "well",
            "wait", "alright", "honestly", "no", "god", "man",
        }
        if first in reaction_starters:
            return "reaction"

        # Mid-thought: starts lowercase or with a conjunction
        mid_thought_starters = {"and", "but", "because", "which", "that", "though"}
        if text[0].islower() or first in mid_thought_starters:
            return "mid-thought"

        # Fact: starts with a number or measurement
        if re.match(r"^\d", text):
            return "fact"

        return "statement"

    return "statement"


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT_TEMPLATE = """\
You are writing a ~2 minute audio snippet (roughly 280-320 words) \
between two co-hosts discussing a piece of news.

Show: {show}
Show personality:
{personality}

THE HOSTS
Both hosts are equally informed and equally curious. They are \
peers, not interviewer and expert. Neither one is the "smart one" \
or the "audience surrogate." Think of two well-read friends \
catching each other up on something they both find interesting.

CONVERSATIONAL TEXTURE
Real conversations between informed peers include some mix of \
the following — but never all of them, and never in a predictable \
order. Pick what serves the specific story:
- Stating facts (both hosts do this, not just one)
- Reacting before adding ("Oh that's wild -" / "Yeah, and...")
- Mild disagreement or alternative framing
- Building on the other's point with a related fact
- Brief tangents or comparisons ("Reminds me of...")
- Shared uncertainty ("I'm honestly not sure what to make of...")
- Half-finished thoughts the other picks up
- Light humor where it fits the topic
- Acknowledging when something is genuinely surprising

WHAT TO AVOID
- Question-answer ping pong
- "What do you think about..." or "Can you explain..." openers
- One host playing dumb so the other can explain
- Both hosts agreeing on everything the same way
- Wrapping with a tidy moral or takeaway every time
- Predictable opening or closing patterns

OPENINGS AND CLOSINGS
Vary wildly. Sometimes start mid-thought. Sometimes with a \
reaction. Sometimes with a fact. Rarely with a question. Endings \
can be a punchline, a quiet observation, unresolved tension, a \
callback, or a "we'll see." Not always a summary.

TONE
Match the topic. A trade rumor is louder than a Mars discovery. \
A health study is more measured than a tech launch. Let the \
content set the energy. Match the show personality above exactly.

CONVERSATION RULES
- Use fragments and incomplete sentences — not every line needs \
to be grammatically complete.
- Include natural fillers where they fit: like, honestly, I mean, \
look, so, yeah, right.
- Write interruptions by ending a line with an ASCII hyphen (-). \
This means that voice got cut off by the other. Use a plain hyphen \
only, not an em dash.
- Every line must add something: a fact, a reaction, an implication, \
a counterpoint. No filler.
- Reference something said earlier in the snippet (callbacks).

BANNED PHRASES — never use these under any circumstances:
"this is wild", "you won't believe", "get this", "here's the thing",
"in other news", "meanwhile", "moving on",
"Hey listeners", "Welcome back", "Today we're discussing",
"well, we'll see what happens", "only time will tell", "time will tell",
"running", "exercising", "commuting", "workout", "on your run",
"and that's pretty crazy if you think about it", "honestly though",
"wow", "incredible", "amazing", "fascinating",
any forced enthusiasm or hype language, any morning-show energy

BANNED WRAP-UPS
Do not end with summary statements, calls to action, or tidy conclusions.
End mid-conversation, with the last thought still hanging.

FORMAT
Label each line with A: or B:
No stage directions, no [laughs], no narration.\
"""

_USER_TEMPLATE = """\
Turn this article into a ~2 minute dialogue (280-320 words total) between A and B.

Title: {title}
Source: {source}
Summary: {description}
Content: {content}

Energy for this one: {energy}
{avoid_patterns_line}
Write only the dialogue. Each line must start with "A:" or "B:".\
"""

# ---------------------------------------------------------------------------
# Quality filter
# ---------------------------------------------------------------------------
_QUALITY_FILTER_PHRASES = [
    "could not generate",
    "unable to summarize",
    "i cannot",
    "i am unable",
    "sorry, i",
    "sorry i",
    "as an ai",
    "i do not have enough information",
    "the article does not provide",
]


def summarize_article(article: dict, category: str = "unknown") -> str | None:
    """
    Use Claude to turn a raw article dict into a ~280-320 word dialogue script.

    The script is formatted as lines prefixed "A:" or "B:".
    Returns the script string on success, None on failure or quality filter rejection.
    """
    api_key = settings.anthropic_api_key.strip()
    if not api_key or api_key.lower() in ("none", ""):
        logger.warning("ANTHROPIC_API_KEY is not configured. Cannot summarize.")
        return None

    voice_pair = get_voice_pair(category)
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
        show=voice_pair["show"],
        personality=voice_pair["personality"],
    )

    # B) Random energy injection
    energy = random.choice(_ENERGY_OPTIONS)

    # C) Opening-pattern avoidance
    if _recent_opening_patterns:
        patterns_str = ", ".join(dict.fromkeys(_recent_opening_patterns))  # deduped, ordered
        avoid_patterns_line = f"Avoid these opening patterns for this snippet: {patterns_str}"
    else:
        avoid_patterns_line = ""

    prompt = _USER_TEMPLATE.format(
        title=article.get("title", ""),
        source=article.get("source", "Unknown"),
        description=article.get("description", ""),
        content=(article.get("content") or "")[:2000],
        energy=energy,
        avoid_patterns_line=avoid_patterns_line,
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            system=system_prompt,
        )
        script = message.content[0].text.strip()

        # Quality filter: reject refusal or error responses
        script_lower = script.lower()
        for phrase in _QUALITY_FILTER_PHRASES:
            if phrase in script_lower:
                logger.warning(
                    "Rejecting script for '%s' — contains disallowed phrase: '%s'",
                    article.get("title", "")[:60],
                    phrase,
                )
                return None

        # C) Record opening pattern for next call
        pattern = _detect_opening_pattern(script)
        _recent_opening_patterns.append(pattern)

        word_count = len(script.split())
        logger.info(
            "Dialogue script for '%s' (show=%s, energy=%s, opening=%s): %d words.",
            article.get("title", "")[:60],
            voice_pair["show"],
            energy,
            pattern,
            word_count,
        )
        return script

    except anthropic.AuthenticationError:
        logger.error("Anthropic authentication failed. Check ANTHROPIC_API_KEY.")
        return None
    except anthropic.RateLimitError:
        logger.warning("Anthropic rate limit hit. Will retry next cycle.")
        return None
    except anthropic.APIStatusError as exc:
        logger.error("Anthropic API error: %s", exc)
        return None
    except Exception as exc:
        logger.exception("Unexpected error summarizing article: %s", exc)
        return None
