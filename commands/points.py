import discord

points = {}

def setup(bot):
    @bot.tree.command(name="points", description="Check a member's points")
    async def points_cmd(interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        balance = points.get(member.id, 0)
        await interaction.response.send_message(f"{member.display_name} has {balance} points.")

    @bot.tree.command(name="add", description="Add points to a member")
    async def add_cmd(interaction: discord.Interaction, member: discord.Member, amount: int):
        allowed_roles = ["Moderator", "Elder"]
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ Only Moderators and Elders can add points.", ephemeral=True)
            return
        points[member.id] = points.get(member.id, 0) + amount
        await interaction.response.send_message(f"✅ Added {amount} points to {member.display_name}.")
