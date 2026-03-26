import discord
from discord.ext import commands
from discord import app_commands

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        # Sync commands automatically
        await self.tree.sync()

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # Handle cooldown errors globally
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏳ Please wait {error.retry_after:.1f} seconds before using `{interaction.command.name}` again.",
                ephemeral=True
            )
        else:
            # Fallback for other errors
            if interaction.response.is_done():
                await interaction.followup.send("❌ An unexpected error occurred.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ An unexpected error occurred.", ephemeral=True)

# Example Cog with your price command
class PriceCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="price", description="Check WEMIX & USDT price in PHP and USD")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)  # 1 use per 10s per user
    async def price_cmd(self, interaction: discord.Interaction):
        # Your price logic here (with retry, etc.)
        await interaction.response.send_message("💰 Price command executed!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PriceCog(bot))
