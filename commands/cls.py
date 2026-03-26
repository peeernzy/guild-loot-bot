import discord
import asyncio


def setup(bot):
    @bot.tree.command(name="cls", description="Clear ALL messages in current channel (bot included). Only Moderator/Elder.")
    async def cls_cmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        # Purge ALL messages including bot (limit=None clears up to 14 days history)
        deleted = await interaction.channel.purge(limit=None, check=lambda m: not m.pinned)

        await interaction.response.send_message(f"✅ Cleared {len(deleted)} messages. Use again for full wipe.", ephemeral=True)

