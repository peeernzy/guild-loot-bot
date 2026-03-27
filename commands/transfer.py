import discord
from .utils import get_points, spend_points, add_points
from .logger import log_event

def setup(bot):
    @bot.tree.command(name="transfer", description="Transfer your points to another player")
    async def transfer_cmd(interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive.", ephemeral=True)
            return
        sender_id = interaction.user.id
        if sender_id == member.id:
            await interaction.response.send_message("❌ Cannot transfer to self.", ephemeral=True)
            return

        sender_pts = get_points(sender_id)
        if sender_pts < amount:
            await interaction.response.send_message("❌ Insufficient points.", ephemeral=True)
            return

        spend_points(sender_id, amount, "transfer")
        add_points(member.id, amount)
        log_event("transfer", sender_id, f"to {member.display_name}", amount)

        await interaction.response.send_message(
            f"✅ **{interaction.user.display_name}** transferred **{amount} pts** to **{member.display_name}**!\n"
            f"{interaction.user.mention} now: `{sender_pts - amount}` | {member.mention}: updated"
        )

