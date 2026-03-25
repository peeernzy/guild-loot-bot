import discord


def setup(bot):
    @bot.tree.command(name="cls", description="Clear recent messages in the current channel")
    async def cls_cmd(interaction: discord.Interaction, amount: int = 100):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message(
                "❌ Only Moderators and Elders can use /cls.",
                ephemeral=True
            )
            return

        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message(
                "❌ This command can only be used in a text channel.",
                ephemeral=True
            )
            return

        amount = max(1, min(amount, 100))

        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(
            f"🧹 Cleared {len(deleted)} messages from {interaction.channel.mention}.",
            ephemeral=True
        )
