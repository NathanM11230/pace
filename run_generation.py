from app.database import SessionLocal
from app.services.content_generator import generate_daily_content

print("Starting content generation...")
db = SessionLocal()
try:
    result = generate_daily_content(db)
    print(f"\nResult: {result}")
finally:
    db.close()