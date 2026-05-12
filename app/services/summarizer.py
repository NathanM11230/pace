import logging

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a writer creating short audio scripts that sound like a real person sharing something \
they genuinely find interesting — not a podcast host, not a news anchor, just a person talking.

Rules you must follow without exception:
- Use contractions throughout: it's, they're, we've, don't, isn't, there's
- Match tone to topic: serious news gets a measured tone, lighter stories get more ease
- Use specific numbers and concrete details, never vague claims
- Vary sentence length naturally — short punchy sentences mixed with longer ones
- Sparingly use natural fillers like "actually", "turns out", or "apparently" — but not more than once per script
- 150-180 words total, no more, no less

Banned phrases — never use these under any circumstances:
"Hey listeners", "Welcome back", "So today we're talking about", "This is wild", \
"You won't believe", "Get this", "Here's the thing", "Well, we'll see what happens", \
"Only time will tell", "Time will tell", "In other news", "Meanwhile", \
"running", "exercising", "commuting", "workout", "on your run", \
any forced enthusiasm or hype language

Opening — rotate naturally between these styles, never repeating the same pattern twice in a row:
- Drop straight into the news: "Google just announced..."
- Start with a question: "What happens when..."
- Lead with the stakes: "If this works, it could change..."
- Open with context: "For years, scientists have wondered..."
- Begin with a specific number or fact: "Three thousand people..."
- Start with the human angle: "A team in Tokyo just figured out..."

Structure:
1. Open with the most interesting angle using one of the styles above
2. Give the key information and context
3. End with a specific detail or observation that makes you think — NOT a summary, NOT a call to action

Write ONLY the script. No labels, no headers, no meta-commentary.\
"""

_USER_TEMPLATE = """\
Turn this article into a 60-second audio script (150-180 words).

Title: {title}
Source: {source}
Summary: {description}
Content: {content}

Write the script now.\
"""

_QUALITY_FILTER_PHRASES = [
    "could not generate",
    "unable to summarize",
    "i cannot",
    "i am unable",
    "sorry, i",
    "as an ai",
    "i do not have enough information",
    "the article does not provide",
]


def summarize_article(article: dict) -> str | None:
    """
    Use the Anthropic Claude API to turn a raw article dict into a
    ~150-180 word conversational running script.

    Returns the script string on success, None on failure.
    """
    api_key = settings.anthropic_api_key.strip()
    if not api_key or api_key.lower() in ("none", ""):
        logger.warning("ANTHROPIC_API_KEY is not configured. Cannot summarize.")
        return None

    prompt = _USER_TEMPLATE.format(
        title=article.get("title", ""),
        source=article.get("source", "Unknown"),
        description=article.get("description", ""),
        content=(article.get("content") or "")[:2000],  # trim to avoid huge contexts
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
            system=_SYSTEM_PROMPT,
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
            "Summarized article '%s' -> %d words.",
            article.get("title", "")[:60],
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
