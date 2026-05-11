from app.services.news_fetcher import CATEGORIES

print("Categories defined:")
for category, queries in CATEGORIES.items():
    print(f"  {category}: {queries}")
print(f"\nTotal categories: {len(CATEGORIES)}")