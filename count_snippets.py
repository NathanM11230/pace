import sqlite3

conn = sqlite3.connect('pace.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM snippets")
count = cursor.fetchone()[0]

print(f"Total snippets: {count}")

conn.close()