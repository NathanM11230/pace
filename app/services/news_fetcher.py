import logging
import re

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
    "tech": ["big tech company announcement", "software product launch"],
    "startups": ["startup funding round", "venture capital startup"],
    "gadgets": ["new smartphone release", "new laptop release"],
    "gaming": ["new video game release", "gaming news PC console"],
    "nba": ["NBA basketball", "NBA games"],
    "nfl": ["NFL football", "NFL news"],
    "soccer": ["soccer news", "premier league"],
    "mlb": ["MLB baseball", "baseball news"],
    "us_politics": ["US politics", "congress news"],
    "world_news": ["global conflict diplomacy", "international politics crisis"],
    "business": ["company earnings merger acquisition", "CEO executive business"],
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
    "history": ["archaeological discovery", "historical research findings"],
    "psychology": ["psychology research", "mental health"],
}

_NEWSDATA_BASE = "https://newsdata.io/api/1/latest"

# Maps Pace categories to NewsData.io category filter values.
# None means no category filter (query alone is sufficient).
_NEWSDATA_CATEGORY_MAP: dict[str, str | None] = {
    "ai": "technology",
    "tech": "technology",
    "startups": "technology",
    "gadgets": "technology",
    "gaming": "entertainment",
    "nba": "sports",
    "nfl": "sports",
    "soccer": "sports",
    "mlb": "sports",
    "us_politics": "politics",
    "world_news": "world",
    "business": "business",
    "markets": "business",
    "space": "science",
    "health": "health",
    "climate": "environment",
    "science": "science",
    "movies": "entertainment",
    "tv": "entertainment",
    "music": "entertainment",
    "food": "food",
    "travel": "tourism",
    "true_crime": "crime",
    "history": None,
    "psychology": "health",
}


def fetch_articles(category: str, query: str, max_articles: int = 3) -> list[dict]:
    """
    Fetch up to *max_articles* articles from NewsData.io for the given query.

    Uses the /latest endpoint which returns the most recent articles.

    Returns a list of article dicts on success, an empty list on any error.
    """
    api_key = settings.newsdata_api_key.strip()
    if not api_key or api_key.lower() in ("demo", "none", ""):
        logger.warning(
            "NEWSDATA_API_KEY is not configured. Skipping fetch for query '%s'.", query
        )
        return []

    newsdata_category = _NEWSDATA_CATEGORY_MAP.get(category)
    params: dict = {
        "q": query,
        "language": "en",
        "country": "us",
        "size": min(max_articles * 5, 10),  # fetch extra to absorb filter rejects
        "apikey": api_key,
    }
    if newsdata_category:
        params["category"] = newsdata_category

    try:
        response = requests.get(_NEWSDATA_BASE, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        articles = data.get("results", [])
        if not articles:
            logger.info("No articles found for query '%s'.", query)
            return []

        results: list[dict] = []
        for article in articles[:max_articles]:
            # Skip articles with missing essential fields
            if not article.get("title") or not article.get("link"):
                continue

            title = article.get("title", "")
            description = article.get("description") or ""
            raw_content = article.get("content") or ""
            content = raw_content if raw_content and "ONLY AVAILABLE" not in raw_content else description
            title_lower = title.lower()
            combined = (title + " " + description + " " + content).lower()
            source_name = article.get("source_name", "")

            # 1. Skip thin descriptions
            if len(description) < 100:
                logger.info("Skipping short description: '%s'", title[:60])
                continue

            # 2. Skip unreliable sources
            if source_name in _UNRELIABLE_SOURCES:
                logger.info("Skipping unreliable source '%s'.", source_name)
                continue

            # 3. Skip sponsored/promotional/supplement content
            if any(phrase in title_lower for phrase in _SPAM_PHRASES):
                logger.info("Skipping spam article: '%s'", title[:60])
                continue

            # 4. Skip social media posts (titles with hashtags)
            if "#" in title:
                logger.info("Skipping social media post: '%s'", title[:60])
                continue

            # 5. Skip software/driver release notes (version numbers like 1.2.3.4)
            if _VERSION_RE.search(title):
                logger.info("Skipping software release article: '%s'", title[:60])
                continue

            results.append(
                {
                    "title": title,
                    "description": description,
                    "content": content,
                    "url": article.get("link", ""),
                    "source": source_name or "Unknown",
                    "publishedAt": article.get("pubDate", ""),
                    "category": category,
                    "query": query,
                }
            )

        logger.info(
            "Fetched %d articles for category='%s', query='%s'.",
            len(results), category, query,
        )
        return results

    except requests.exceptions.Timeout:
        logger.error("Timeout while fetching articles for query '%s'.", query)
        return []
    except requests.exceptions.HTTPError as exc:
        logger.error("HTTP error fetching articles for query '%s': %s", query, exc)
        return []
    except Exception as exc:
        logger.exception("Unexpected error fetching articles for query '%s': %s", query, exc)
        return []
