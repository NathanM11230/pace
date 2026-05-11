import logging
from app.database import SessionLocal
from app.services.content_generator import generate_daily_content

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print("Starting content generation with verbose logging...")
db = SessionLocal()
try:
    result = generate_daily_content(db)
    print(f"\n? DONE!")
    print(f"Result: {result}")
finally:
    db.close()