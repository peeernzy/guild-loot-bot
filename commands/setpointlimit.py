import discord

WEEKLY_LIMIT = 35  # Global weekly spend limit - Moderator changeable

def setup(bot):
    @bot.tree.command(name="setpointlimit", description="Set weekly point spend limit for claims/bids")
    @discord.app_commands.describe(limit="Max points spendable per week (default 35)")
    async def setpointlimit_cmd(interaction: discord.Interaction, limit: int = 35):
        allowed_roles
