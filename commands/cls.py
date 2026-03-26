import discord
from discord.ext import commands

class ClearCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="cls",
        description="Clear ALL messages in current channel (bot included). Only Moderator/Elder."
    )
    async def cls_cmd(self, interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        # Defer immediately so the interaction doesn't expire
        await interaction.response.defer(ephemeral=True)

        # Purge ALL messages including bot (limit=None clears up to 14 days history)
        deleted = await interaction.channel.purge(limit=None, check=lambda m: not m.pinned)

        # Send result after purge
        await interaction.followup.send(
            f"✅ Cleared {len(deleted)} messages. Use again for full wipe.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ClearCog(bot))
