from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

print("Adding chord columns...")

cur.execute("""
    ALTER TABLE songs
    ADD COLUMN IF NOT EXISTS chords TEXT NOT NULL DEFAULT '';
""")

cur.execute("""
    ALTER TABLE songs
    ADD COLUMN IF NOT EXISTS chord_key VARCHAR(3) NOT NULL DEFAULT 'C';
""")

cur.execute("""
    ALTER TABLE songs
    ADD COLUMN IF NOT EXISTS chords_enabled BOOLEAN NOT NULL DEFAULT FALSE;
""")

conn.commit()

print("Chord columns added successfully.")

cur.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'songs'
    ORDER BY ordinal_position
""")

print("SONGS TABLE COLUMNS:")
print([row[0] for row in cur.fetchall()])

cur.execute("SELECT COUNT(*) FROM songs")
print("SONGS:", cur.fetchone()[0])

cur.close()
conn.close()