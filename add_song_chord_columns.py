import sqlite3

DB_PATH = "instance/app.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check existing columns
columns = [
    row[1]
    for row in cursor.execute("PRAGMA table_info(songs)").fetchall()
]

print("Existing songs columns:")
print(columns)

# Add chords column if missing
if "chords" not in columns:
    cursor.execute(
        "ALTER TABLE songs ADD COLUMN chords TEXT"
    )
    print("Added: chords")
else:
    print("Already exists: chords")

# Add chord_key column if missing
if "chord_key" not in columns:
    cursor.execute(
        "ALTER TABLE songs ADD COLUMN chord_key VARCHAR(20)"
    )
    print("Added: chord_key")
else:
    print("Already exists: chord_key")

# Add chords_enabled column if missing
if "chords_enabled" not in columns:
    cursor.execute(
        "ALTER TABLE songs ADD COLUMN chords_enabled BOOLEAN NOT NULL DEFAULT 0"
    )
    print("Added: chords_enabled")
else:
    print("Already exists: chords_enabled")

conn.commit()

print("\nUpdated songs table:")
print(
    cursor.execute(
        "PRAGMA table_info(songs)"
    ).fetchall()
)

# Confirm existing songs are still there
count = cursor.execute(
    "SELECT COUNT(*) FROM songs"
).fetchone()[0]

print(f"\nTotal songs preserved: {count}")

conn.close()

print("\nSong chord columns migration completed successfully.")