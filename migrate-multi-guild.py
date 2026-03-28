import sqlite3
from pathlib import Path
import os

# DB path from points.py
APP_DATA_DIR = Path(os.getenv("APPDATA", Path.home() / ".guild-loot-bot")) / "guild-loot-bot"
SQLITE_DB_FILE = APP_DATA_DIR / "points.sqlite3"

print(f"Connecting to DB: {SQLITE_DB_FILE}")

conn = sqlite3.connect(SQLITE_DB_FILE)
cur = conn.cursor()

# Check if items table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items';")
if not cur.fetchone():
    print("❌ No 'items' table found. Run /impitems first.")
    conn.close()
    exit(1)

# Check if guild_id column exists
cur.execute("PRAGMA table_info(items)")
columns = [row[1] for row in cur.fetchall()]
if 'guild_id' in columns:
    print("✅ guild_id column already exists.")
else:
    # Add guild_id column
    cur.execute("ALTER TABLE items ADD COLUMN guild_id TEXT")
    print("✅ Added guild_id column.")

conn.commit()
conn.close()
print("✅ Migration complete!")
