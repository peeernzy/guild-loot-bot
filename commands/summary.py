import discord
from .points import points

def setup(bot):
    @bot.tree.command(name="summary", description="Show all balances")
    async def summary_cmd(interaction: discord.Interaction):
        if not points:
            await interaction.response.send_message("No points recorded yet.")
            return
        summary = "\n".join([
            f"{interaction.guild.get_member(uid).display_name}: {pts}"
            for uid, pts in points.items()
            if interaction.guild.get_member(uid) is not None
        ])
        await interaction.response.send_message(f"📊 Points Summary:\n{summary}")
