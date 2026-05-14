"""Delete all snippets from the DB and remove their audio files."""
from pathlib import Path
from app.database import SessionLocal
from app.models import Snippet

db = SessionLocal()
try:
    snippets = db.query(Snippet).all()
    print(f"Found {len(snippets)} snippets to delete.")
    for s in snippets:
        if s.audio_file:
            p = Path(s.audio_file)
            if p.exists():
                p.unlink()
        db.delete(s)
    db.commit()
    print("Done — all snippets cleared.")
finally:
    db.close()
