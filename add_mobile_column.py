import sqlite3

DB_PATH = "instance/app.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Add the legacy mobile column required by the current SQLAlchemy model
cursor.execute(
    "ALTER TABLE users ADD COLUMN mobile VARCHAR(20)"
)

# Give the existing account an internal legacy value.
# This is NOT used for login or OTP.
cursor.execute(
    "UPDATE users SET mobile = ? WHERE id = ?",
    ("legacy-user-1", 1)
)

conn.commit()

print("Users table:")
print(cursor.execute("PRAGMA table_info(users)").fetchall())

print("\nExisting users:")
print(
    cursor.execute(
        "SELECT id, username, mobile, is_verified FROM users"
    ).fetchall()
)

conn.close()

print("\nMobile column migration completed successfully.")