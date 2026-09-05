import sqlite3

DB_PATH = "instance/app.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Rename the old email column to username
cursor.execute(
    "ALTER TABLE users RENAME COLUMN email TO username"
)

# Convert the existing account
cursor.execute(
    "UPDATE users SET username = ?, is_verified = 1 WHERE id = ?",
    ("abhishek", 1)
)

conn.commit()

print("Users table:")
print(cursor.execute("PRAGMA table_info(users)").fetchall())

print("\nExisting users:")
print(
    cursor.execute(
        "SELECT id, username, is_verified FROM users"
    ).fetchall()
)

conn.close()

print("\nMigration completed successfully.")