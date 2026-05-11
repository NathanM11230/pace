import logging

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a writer creating short, engaging audio scripts. "
    "Write in a natural, conversational tone—like telling a friend an interesting story. "
    "Keep it to approximately 150-180 words. "
    "Jump straight into the story without any greeting or intro phrase."
)

_USER_TEMPLATE = """\
Summarize this article as a 60-second audio snippet. Requirements:
- Conversational, engaging tone that hooks the listener immediately
- Around 150-180 words (reads in ~60 seconds at normal pace)
- Start with a strong hook, not a generic intro
- Do NOT mention running, exercising, commuting, or any specific activity
- Do NOT say things like "Hey listeners" or "Welcome"
- Write like you are telling a friend an interesting story
- Use natural speech patterns (contractions, casual language)
- End with a strong closing thought, not a call to action
- Focus on the most interesting or surprising element of the story

Title: {title}
Source: {source}
Summary: {description}
Content: {content}

Write ONLY the audio script, nothing else."""


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
