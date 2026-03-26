import discord
from .points import get_all_points

def setup(bot):
    @bot.tree.command(name="allclanpoints", description="Show all clan member points balances")
    async def allclanpoints_cmd(interaction: discord.Interaction):
        points = get_all_points()
        if not points:
            await interaction.response.send_message("No points recorded yet.")
            return

        entries = [
            (interaction.guild.get_member(int(uid)), pts)
            for uid, pts in points.items()
            if interaction.guild.get_member(int(uid)) is not None
        ]

        if not entries:
            await interaction.response.send_message("No valid members with points found.")
            return

        entries.sort(key=lambda x: x[1], reverse=True)
        summary_lines = [f"{member.display_name}: {pts}" for member, pts in entries]
        summary_text = "\n".join(summary_lines)

        await interaction.response.send_message(f"📊 Points Summary:\n{summary_text}")
