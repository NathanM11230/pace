import logging
import re
from datetime import datetime, timedelta, timezone

import requests

from app.config import settings

logger = logging.getLogger(__name__)

_UNRELIABLE_SOURCES = {"Natural News", "InfoWars", "Breitbart News"}

_SPAM_PHRASES = {
    "sponsored", "advertisement", "promoted", "advertorial",
    "claims evaluated", "claims reviewed", "everyone is researching",
    "bhb", "keto formula", "slimming tea", "detox tea", "burn fat",
    "weight loss formula", "ingredients that work", "diet pill",
    "supplement review", "buy now", "limited offer",
}

# Matches version strings like 1.2.3 or 31.0.101.3959 (software/driver releases)
_VERSION_RE = re.compile(r"\d+\.\d+\.\d+")

CATEGORIES: dict[str, list[str]] = {
    "ai": ["artificial intelligence breakthroughs", "AI research"],
    "tech": ["technology news", "tech industry"],
    "startups": ["startup funding", "tech startups"],
    "gadgets": ["new gadgets", "consumer electronics"],
    "gaming": ["video games", "esports"],
    "nba": ["NBA basketball", "NBA games"],
    "nfl": ["NFL football", "NFL news"],
    "soccer": ["soccer news", "premier league"],
    "mlb": ["MLB baseball", "baseball news"],
    "us_politics": ["US politics", "congress news"],
    "world_news": ["world news", "international news"],
    "business": ["business news", "corporate news"],
    "markets": ["stock market", "financial markets"],
    "space": ["space exploration", "NASA SpaceX"],
    "health": ["health research", "medical breakthroughs"],
    "climate": ["climate change", "environmental news"],
    "science": ["science discoveries", "scientific research"],
    "movies": ["movie news", "film industry"],
    "tv": ["TV shows", "streaming series"],
    "music": ["music industry", "new music releases"],
    "food": ["food trends", "restaurant news"],
    "travel": ["travel news", "tourism"],
    "true_crime": ["true crime stories", "criminal investigations"],
    "history": ["historical discoveries", "history news"],
    "psychology": ["psychology research", "mental health"],
}

_NEWS_API_BASE = "https://newsapi.org/v2/everything"


def fetch_articles(category: str, query: str, max_articles: int = 3) -> list[dict]:
    """
    Fetch up to *max_articles* articles from NewsAPI for the given query.

    Returns a list of article dicts on success, an empty list on any error.
    """
    api_key = settings.news_api_key.strip()
    if not api_key or api_key.lower() in ("demo", "none", ""):
        logger.warning(
            "NEWS_API_KEY is not configured. Skipping fetch for query '%s'.", query
        )
        return []

    # # Only look at articles published in the last 24 hours (disabled for testing)
    # from_date = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime(
    #     "%Y-%m-%dT%H:%M:%SZ"
    # )

    params = {
        "q": query,
        # "from": from_date,  # disabled for testing — fetches articles from any date
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": max_articles,
        "apiKey": api_key,
    }

    try:
        response = requests.get(_NEWS_API_BASE, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        articles = data.get("articles", [])
        if not articles:
            logger.info("No articles found for query '%s'.", query)
            return []

        results: list[dict] = []
        for article in articles[:max_articles]:
            # Skip articles with missing essential fields
            if not article.get("title") or not article.get("url"):
                continue

            title = article.get("title", "")
            description = article.get("description") or ""
            title_lower = title.lower()
            combined = (title + " " + description).lower()
            source_name = article.get("source", {}).get("name", "")

            # 1. Skip thin descriptions
            if len(description) < 100:
                logger.debug("Skipping short description: '%s'", title[:60])
                continue

            # 2. Skip unreliable sources
            if source_name in _UNRELIABLE_SOURCES:
                logger.debug("Skipping unreliable source '%s'.", source_name)
                continue

            # 3. Skip sponsored/promotional/supplement content
            if any(phrase in title_lower for phrase in _SPAM_PHRASES):
                logger.debug("Skipping spam article: '%s'", title[:60])
                continue

            # 4. Skip social media posts (titles with hashtags)
            if "#" in title:
                logger.debug("Skipping social media post: '%s'", title[:60])
                continue

            # 5. Skip software/driver release notes (version numbers like 1.2.3.4)
            if _VERSION_RE.search(title):
                logger.debug("Skipping software release article: '%s'", title[:60])
                continue

            # 6. Skip if none of the query keywords appear in title+description
            query_words = [w.lower() for w in query.split() if len(w) > 3]
            if query_words and not any(w in combined for w in query_words):
                logger.debug("Skipping off-topic article for query '%s': '%s'", query, title[:60])
                continue

            results.append(
                {
                    "title": article.get("title", ""),
                    "description": article.get("description") or "",
                    "content": article.get("content") or "",
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "publishedAt": article.get("publishedAt", ""),
                    "category": category,
                    "query": query,
                }
            )

        logger.info(
            "Fetched %d articles for category='%s', query='%s'.",
            len(results),
            category,
            query,
        )
        return results

    except requests.exceptions.Timeout:
        logger.error("Timeout while fetching articles for query '%s'.", query)
        return []
    except requests.exceptions.HTTPError as exc:
        logger.error(
            "HTTP error fetching articles for query '%s': %s", query, exc
        )
        return []
    except Exception as exc:
        logger.exception(
            "Unexpected error fetching articles for query '%s': %s", query, exc
        )
        return []
