import discord
from .points import reset_all_points
from .loot import claims, leaderboard
from .utils import weekly_spent

def setup(bot):
    @bot.tree.command(name="reset", description="Clear all bot data (Moderator/Elder only)")
    async def reset_cmd(interaction: discord.Interaction):
        allowed_roles = ["Moderator", "Elder"]
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message(
                "❌ Only Moderators and Elders can reset the bot data.",
                ephemeral=True
            )
            print(f"[SECURITY] {interaction.user} tried to use /reset without permission.")
            return

        reset_all_points()
        claims.clear()
        leaderboard.clear()
        weekly_spent.clear()
        # Clear history for testing
        import os
        if os.path.exists("loot_log.json"):
            os.remove("loot_log.json")
        print("loot_log.json cleared")

        await interaction.response.send_message("⚠️ All bot data + history cleared for testing.")
        print(f"[RESET] {interaction.user} cleared all bot data.")
