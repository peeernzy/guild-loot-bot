import discord


def setup(bot):
    @bot.tree.command(name="cls", description="Clear ALL messages in current channel (bot included)")
    async def cls_cmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message(
                "❌ Only Moderators and Elders can use /cls.",
                ephemeral=True
            )
            return

        if interaction.guild is None or interaction.channel is None:
            await interaction.response.send_message(
                "❌ This command can only be used inside a server text channel.",
                ephemeral=True
            )
            return

        await interaction.response.send_message("🧹 Clearing channel...", ephemeral=True, delete_after=3)

        # Delete bot messages first (including this one after defer)
        bot_msgs = []
        async for msg in interaction.channel.history(limit=100):
            if msg.author == interaction.client.user:
                bot_msgs.append(msg)

        for msg in bot_msgs:
            try:
                await msg.delete()
            except:
                pass

        # Purge all other messages (no limit, up to Discord max ~14 days)
        deleted = await interaction.channel.purge(check=lambda m: m.author != interaction.client.user and not m.pinned)

        await interaction.followup.send(
            f"🧹 Cleared entire channel! Deleted bot messages + {len(deleted)} others.",
            ephemeral=True
        )

