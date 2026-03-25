import discord
import asyncio


def setup(bot):
    @bot.tree.command(name="cls", description="Clear ALL messages in current channel (bot included). Only Moderator/Elder.")
    async def cls_cmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            return  # Silent fail for non-permitted

        if interaction.guild is None or interaction.channel is None:
            return

        # Purge ALL messages including bot (limit=None clears up to 14 days history)
        deleted = await interaction.channel.purge(limit=None, check=lambda m: not m.pinned, bulk_delete=True)

        # No response/followup - command invisible

