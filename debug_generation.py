import os
from dotenv import load_dotenv
from app.services.news_fetcher import CATEGORIES, fetch_articles

load_dotenv()

print("Testing content generation step by step...\n")

for category, queries in CATEGORIES.items():
    print(f"\n{'='*60}")
    print(f"Category: {category}")
    print(f"{'='*60}")
    
    for query in queries:
        print(f"\n  Query: '{query}'")
        articles = fetch_articles(category, query, max_articles=2)
        print(f"  Found {len(articles)} articles")
        
        if articles:
            for i, article in enumerate(articles, 1):
                title = article.get('title', 'NO TITLE')
                print(f"    {i}. {title[:60]}")
        else:
            print("    (no articles returned)")
        
        # Stop after first category for testing
        break
    break

print("\n\nIf you see articles above, the fetch is working!")