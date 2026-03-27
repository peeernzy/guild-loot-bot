import discord
from discord.ext import commands
import asyncio

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

        # Check channel validity
        if interaction.channel is None or not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("❌ Cannot clear messages here.", ephemeral=True)
            return

        # Check bot permissions
        if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            await interaction.response.send_message("❌ I don’t have permission to delete messages.", ephemeral=True)
            return

        # Defer response
        await interaction.response.defer(ephemeral=True)

        total_deleted = 0
        try:
            while True:
                # Purge in batches of 100
                deleted = await interaction.channel.purge(limit=100, check=lambda m: not m.pinned)
                batch_count = len(deleted)
                total_deleted += batch_count

                if batch_count == 0:
                    break  # No more messages left

                # Pause briefly to avoid rate limits
                await asyncio.sleep(1.5)

            await interaction.followup.send(
                f"✅ Cleared {total_deleted} messages in total.",
                ephemeral=True
            )

        except discord.NotFound:
            await interaction.followup.send("❌ Channel not found.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ Missing permissions.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Failed due to HTTP error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClearCog(bot))
