import json
import datetime
from commands.points import using_postgres, get_sqlite_connection, get_postgres_connection

def initialize_history():
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        event TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        item TEXT NOT NULL,
                        amount INTEGER
                    )
                """)
            conn.commit()
    else:
        with get_sqlite_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    item TEXT NOT NULL,
                    amount INTEGER
                )
            """)
            conn.commit()

def log_event(event_type, user_id, item, amount=None):
    initialize_history()
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO events (timestamp, event, user_id, item, amount) VALUES (%s, %s, %s, %s, %s)",
                    (datetime.datetime.now().isoformat(), event_type, str(user_id), item, amount)
                )
            conn.commit()
    else:
        with get_sqlite_connection() as conn:
            conn.execute(
                "INSERT INTO events (timestamp, event, user_id, item, amount) VALUES (?, ?, ?, ?, ?)",
                (datetime.datetime.now().isoformat(), event_type, str(user_id), item, amount)
            )
            conn.commit()

def get_recent_history(limit=50):
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT timestamp, event, user_id, item, amount FROM events ORDER BY timestamp DESC LIMIT %s", (limit,))
                rows = cur.fetchall()
        return [{"timestamp": r[0], "event": r[1], "user_id": r[2], "item": r[3], "amount": r[4]} for r in rows]
    else:
        with get_sqlite_connection() as conn:
            rows = conn.execute("SELECT timestamp, event, user_id, item, amount FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        return [{"timestamp": r[1], "event": r[2], "user_id": r[3], "item": r[4], "amount": r[5]} for r in rows]

