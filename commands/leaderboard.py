import discord
from .loot import leaderboard

def setup(bot):
    @bot.tree.command(name="leaderboard", description="Show loot winners leaderboard")
    async def leaderboard_cmd(interaction: discord.Interaction):
        if not leaderboard:
            await interaction.response.send_message("No winners yet.")
            return
        summary = "\n".join([
            f"{interaction.guild.get_member(uid).display_name}: {wins} wins"
            for uid, wins in leaderboard.items()
            if interaction.guild.get_member(uid) is not None
        ])
        await interaction.response.send_message(f"🏆 Loot Leaderboard:\n{summary}")
