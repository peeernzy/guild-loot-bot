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

        # Clear history DB table
        from .logger import using_postgres, get_sqlite_connection, get_postgres_connection
        if using_postgres():
            with get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM events")
                conn.commit()
        else:
            with get_sqlite_connection() as conn:
                conn.execute("DELETE FROM events")
                conn.commit()
        print("Events history cleared")


        await interaction.response.send_message("⚠️ All bot data + history cleared for testing.")
        print(f"[RESET] {interaction.user} cleared all bot data.")
