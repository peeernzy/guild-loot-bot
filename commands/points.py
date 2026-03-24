import discord

# =========================
# STORAGE
# =========================
points = {}

# =========================
# CORE FUNCTIONS (USED BY utils.py)
# =========================
def get_points(member_id: int) -> int:
    return points.get(member_id, 0)

def add_points(member_id: int, amount: int):
    points[member_id] = points.get(member_id, 0) + amount
    return points[member_id]

def deduct_points(member_id: int, amount: int):
    points[member_id] = max(0, points.get(member_id, 0) - amount)
    return points[member_id]

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

        allowed_roles = ["Moderator", "Elder"]
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