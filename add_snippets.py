import sqlite3
from datetime import datetime

conn = sqlite3.connect('pace.db')
cursor = conn.cursor()

# Add 3 test snippets
snippets = [
    ('tech', 'OpenAI Releases GPT-5', 'TechCrunch', 'https://example.com/article1', '2026-04-02',
     'OpenAI just dropped GPT-5 and the tech world is buzzing. This model can write entire apps from scratch and reason through complex problems way better than GPT-4.', 
     150, 'test_audio_1.mp3', datetime.now(), True),
    
    ('nba', 'Cavaliers Win in Overtime', 'ESPN', 'https://example.com/article2', '2026-04-02',
     'The Cavs just pulled off an absolute nail biter against the Celtics. Donovan Mitchell hit the game winner with 12 seconds left in OT. Final score 118 to 112.', 
     145, 'test_audio_2.mp3', datetime.now(), True),
    
    ('space', 'NASA Discovers Water on Mars', 'NASA', 'https://example.com/article3', '2026-04-02',
     'NASA scientists just made a discovery that could change space exploration. They found water ice on Mars in areas that actually get sunlight.', 
     160, 'test_audio_3.mp3', datetime.now(), True),
]

for snippet in snippets:
    cursor.execute('''
        INSERT INTO snippets (category, title, source, article_url, published_at, script, word_count, audio_file, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', snippet)

conn.commit()

# Ch