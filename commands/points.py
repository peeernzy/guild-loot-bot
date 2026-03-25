import discord
import json
import os
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    import psycopg

APP_DATA_DIR = Path(os.getenv("APPDATA", Path.home() / ".guild-loot-bot")) / "guild-loot-bot"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

SQLITE_DB_FILE = APP_DATA_DIR / "points.sqlite3"
LEGACY_JSON_FILES = [
    Path("data/points_data.json"),
    Path("points_data.json"),
]


def _normalize_database_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme == "postgres":
        return url.replace("postgres://", "postgresql://", 1)
    return url


def using_postgres() -> bool:
    return bool(DATABASE_URL)


def get_sqlite_connection():
    return sqlite3.connect(SQLITE_DB_FILE)


def get_postgres_connection():
    return psycopg.connect(_normalize_database_url(DATABASE_URL))


def initialize_database():
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS points (
                        member_id TEXT PRIMARY KEY,
                        balance INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )
            conn.commit()
    else:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS points (
                    member_id TEXT PRIMARY KEY,
                    balance INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.commit()


def has_any_points() -> bool:
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM points LIMIT 1")
                row = cur.fetchone()
        return row is not None

    with get_sqlite_connection() as conn:
        row = conn.execute("SELECT 1 FROM points LIMIT 1").fetchone()
    return row is not None


def migrate_legacy_points():
    if has_any_points():
        return

    for legacy_file in LEGACY_JSON_FILES:
        if not legacy_file.exists():
            continue

        try:
            with open(legacy_file, "r") as f:
                legacy_points = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        if using_postgres():
            with get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    for member_id, balance in legacy_points.items():
                        cur.execute(
                            """
                            INSERT INTO points (member_id, balance)
                            VALUES (%s, %s)
                            ON CONFLICT (member_id) DO UPDATE
                            SET balance = EXCLUDED.balance
                            """,
                            (str(member_id), int(balance)),
                        )
                conn.commit()
        else:
            with get_sqlite_connection() as conn:
                for member_id, balance in legacy_points.items():
                    conn.execute(
                        """
                        INSERT INTO points (member_id, balance)
                        VALUES (?, ?)
                        ON CONFLICT(member_id) DO UPDATE SET balance = excluded.balance
                        """,
                        (str(member_id), int(balance)),
                    )
                conn.commit()
        break


initialize_database()
migrate_legacy_points()


def get_all_points() -> dict[str, int]:
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT member_id, balance FROM points ORDER BY balance DESC")
                rows = cur.fetchall()
    else:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                "SELECT member_id, balance FROM points ORDER BY balance DESC"
            ).fetchall()

    return {member_id: balance for member_id, balance in rows}


def get_points(member_id: int) -> int:
    """Return current balance for a member ID."""
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT balance FROM points WHERE member_id = %s",
                    (str(member_id),),
                )
                row = cur.fetchone()
        return row[0] if row else 0

    with get_sqlite_connection() as conn:
        row = conn.execute(
            "SELECT balance FROM points WHERE member_id = ?",
            (str(member_id),),
        ).fetchone()
    return row[0] if row else 0


def set_points(member_id: int, amount: int) -> int:
    """Set a member's points and return the stored balance."""
    safe_amount = max(0, int(amount))

    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO points (member_id, balance)
                    VALUES (%s, %s)
                    ON CONFLICT (member_id) DO UPDATE
                    SET balance = EXCLUDED.balance
                    """,
                    (str(member_id), safe_amount),
                )
            conn.commit()
        return safe_amount

    with get_sqlite_connection() as conn:
        conn.execute(
            """
            INSERT INTO points (member_id, balance)
            VALUES (?, ?)
            ON CONFLICT(member_id) DO UPDATE SET balance = excluded.balance
            """,
            (str(member_id), safe_amount),
        )
        conn.commit()
    return safe_amount


def add_points(member_id: int, amount: int) -> int:
    """Add points to a member ID and return new balance."""
    new_balance = get_points(member_id) + int(amount)
    return set_points(member_id, new_balance)


def deduct_points(member_id: int, amount: int) -> int:
    """Deduct points from a member ID (never below 0)."""
    new_balance = max(0, get_points(member_id) - int(amount))
    return set_points(member_id, new_balance)


def reset_all_points():
    """Clear all saved point balances."""
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM points")
            conn.commit()
        return

    with get_sqlite_connection() as conn:
        conn.execute("DELETE FROM points")
        conn.commit()


def save_points():
    """Compatibility helper for older modules. Database writes are immediate."""
    return None


def setup(bot):

    @bot.tree.command(name="points", description="Check point balance")
    async def points_cmd(interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        balance = get_points(member.id)

        await interaction.response.send_message(
            f"💰 {member.display_name} has {balance} points."
        )

    @bot.tree.command(name="add", description="Add points to a member")
    async def add_cmd(interaction: discord.Interaction, member: discord.Member, amount: int):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message(
                "❌ Only Moderators and Elders can add points.",
                ephemeral=True
            )
            return

        new_balance = add_points(member.id, amount)

        await interaction.response.send_message(
            f"✅ Added {amount} points to {member.display_name}.\n"
            f"💰 New Balance: {new_balance}"
        )
