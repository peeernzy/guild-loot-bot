import discord
from .points import points

def setup(bot):
    # ADD command
    @bot.tree.command(name="add", description="Add points to yourself")
    async def add_cmd(interaction: discord.Interaction, amount: int):
        uid = interaction.user.id
        points[uid] = points.get(uid, 0) + amount
        await interaction.response.send_message(
            f"✅ Added {amount} points to {interaction.user.display_name}.\n"
            f"💰 New Balance: {points[uid]}"
        )

    # POINTS command
    @bot.tree.command(name="points", description="Check your balance")
    async def points_cmd(interaction: discord.Interaction):
        uid = interaction.user.id
        balance = points.get(uid, 0)
        await interaction.response.send_message(
            f"💰 {interaction.user.display_name} has {balance} points."
        )

    # SUMMARY command
    @bot.tree.command(name="summary", description="Show all balances")
    async def summary_cmd(interaction: discord.Interaction):
        # --- MIGRATION STEP ---
        migrated = {}
        for key, pts in list(points.items()):
            if isinstance(key, str):  # old username-based keys
                member = discord.utils.get(interaction.guild.members, name=key)
                if member:
                    migrated[member.id] = migrated.get(member.id, 0) + pts
                del points[key]
            else:
                migrated[key] = migrated.get(key, 0) + pts
        points.update(migrated)

        # --- SUMMARY DISPLAY ---
        if not points:
            await interaction.response.send_message("No points recorded yet.")
            return

        entries = [
            (interaction.guild.get_member(uid), pts)
            for uid, pts in points.items()
            if interaction.guild.get_member(uid) is not None
        ]

        if not entries:
            await interaction.response.send_message("No valid members with points found.")
            return

        # Sort by points (descending)
        entries.sort(key=lambda x: x[1], reverse=True)

        summary_lines = [f"{member.display_name}: {pts}" for member, pts in entries]
        summary_text = "\n".join(summary_lines)

        await interaction.response.send_message(f"📊 Points Summary:\n{summary_text}")
