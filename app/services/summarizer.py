import logging
import re

import anthropic

from app.config import settings
from app.services.voice_pairs import get_voice_pair

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT_TEMPLATE = """\
You are writing a short dialogue between two podcast hosts — Voice A and Voice B — for the show "{show}".

Show personality:
{personality}

STRUCTURE:
- Output ONLY lines prefixed with "A:" or "B:". No headers, no stage directions, no meta-commentary.
- 150-180 words total across both voices.
- Voice A handles 60-70% of the talking. Voice B mostly reacts, interjects, or asks questions.
- Each line is one turn. Multiple turns per voice are fine.

CONVERSATION RULES:
- Use fragments and incomplete sentences — not every line needs to be grammatically complete.
- Include natural fillers where they fit: like, honestly, I mean, look, so, yeah, right.
- Write interruptions by ending a line with an ASCII hyphen (-). This means that voice got cut off by the other. Use a plain hyphen only, not an em dash.
- Short reactions on their own line are good: just "Yeah." or "Huh." or "Dude." is a valid line.
- Voice B can occasionally make a weird observation or joke not directly in the article.
- Reference something said earlier in the snippet (callbacks).
- Vary your opening — never start the same way twice in a row.

PERSONALITY:
- Match the show's personality description above exactly.
- Voice A and Voice B should have clearly distinct speech patterns.
- Disagreement and pushback between voices is encouraged.

BANNED PHRASES — never use these under any circumstances:
"this is wild", "you won't believe", "get this", "here's the thing",
"in other news", "meanwhile", "moving on",
"Hey listeners", "Welcome back", "Today we're discussing",
"well, we'll see what happens", "only time will tell", "time will tell",
"running", "exercising", "commuting", "workout", "on your run",
any forced enthusiasm or hype language

BANNED WRAP-UPS:
Do not end with summary statements, calls to action, or tidy conclusions.
End mid-conversation, with the last thought still hanging.\
"""

_USER_TEMPLATE = """\
Turn this article into a 60-second dialogue (150-180 words total) between Voice A and Voice B.

Title: {title}
Source: {source}
Summary: {description}
Content: {content}

Write only the dialogue. Each line must start with "A:" or "B:".\
"""

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
    Use Claude to turn a raw article dict into a ~150-180 word dialogue script.

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

    prompt = _USER_TEMPLATE.format(
        title=article.get("title", ""),
        source=article.get("source", "Unknown"),
        description=article.get("description", ""),
        content=(article.get("content") or "")[:2000],
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
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

        logger.info(
            "Dialogue script for '%s' (show=%s): %d words.",
            article.get("title", "")[:60],
            voice_pair["show"],
            len(script.split()),
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
