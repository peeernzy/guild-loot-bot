import discord
import json
import os
from pathlib import Path

DATA_DIR = Path(os.getenv("BOT_DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

POINTS_FILE = DATA_DIR / "points_data.json"
LEGACY_POINTS_FILE = Path("points_data.json")

# =========================
# STORAGE
# =========================
points = {}

# =========================
# PERSISTENCE
# =========================
def load_points():
    """Load points from JSON file at bot startup."""
    global points

    source_file = POINTS_FILE

    if not POINTS_FILE.exists() and LEGACY_POINTS_FILE.exists():
        source_file = LEGACY_POINTS_FILE

    if source_file.exists():
        with open(source_file, "r") as f:
            points = json.load(f)
    else:
        points = {}

def save_points():
    """Save points to JSON file after each change."""
    with open(POINTS_FILE, "w") as f:
        json.dump(points, f, indent=4)

# Load on import
load_points()

# =========================
# CORE FUNCTIONS (USED BY utils.py or other commands)
# =========================
def get_points(member_id: int) -> int:
    """Return current balance for a member ID."""
    return points.get(str(member_id), 0)

def add_points(member_id: int, amount: int) -> int:
    """Add points to a member ID and return new balance."""
    member_id_str = str(member_id)
    points[member_id_str] = points.get(member_id_str, 0) + amount
    save_points()
    return points[member_id_str]

def deduct_points(member_id: int, amount: int) -> int:
    """Deduct points from a member ID (never below 0)."""
    member_id_str = str(member_id)
    points[member_id_str] = max(0, points.get(member_id_str, 0) - amount)
    save_points()
    return points[member_id_str]

# =========================
# DISCORD COMMANDS
# =========================
def setup(bot):

    # ===== CHECK POINTS =====
    @bot.tree.command(name="points", description="Check a member's points")
    async def points_cmd(interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        balance = get_points(member.id)

        await interaction.response.send_message(
            f"💰 {member.display_name} has {balance} points."
        )

    # ===== ADD POINTS =====
    @bot.tree.command(name="add", description="Add points to a member")
    async def add_cmd(interaction: discord.Interaction, member: discord.Member, amount: int):
        # Only Moderators and Elders can use this
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
