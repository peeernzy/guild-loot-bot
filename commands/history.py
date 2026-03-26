import discord
import datetime
from commands.logger import get_recent_history

def setup(bot):
    @bot.tree.command(name="history", description="View recent winners history")
    @discord.app_commands.describe(limit="Number of recent entries to show (default 10, max 50)")
    async def history_cmd(interaction: discord.Interaction, limit: int = 10):
        if limit > 50:
            limit = 50
        
        history = get_recent_history(limit)
        if not history:
            await interaction.response.send_message("📜 No history yet.")
            return
        
        # Filter wins only
        winners = [e for e in history if e['event'] in ['win', 'award', 'grant']]
        winners.sort(key=lambda x: x['timestamp'], reverse=True)
        recent = winners[:limit]
        
        # Resolve user names
        unique_ids = {entry['user_id'] for entry in recent}
        winner_names = {}
        guild = interaction.guild
        for uid in unique_ids:
            member = guild.get_member(int(uid))
            winner_names[uid] = member.display_name if member else f"Unknown ({uid})"
        
        embed = discord.Embed(
            title="🏆 Winner History",
            color=discord.Color.gold()
        )
        
        for entry in recent:
            timestamp = datetime.datetime.fromisoformat(entry["timestamp"])
            date_str = timestamp.strftime("%Y-%m-%d %H:%M")
            winner_name = winner_names[entry['user_id']]
            type_emoji = "✅" if entry["event"] == "win" else "🎁"
            amount = entry.get('amount', 0)
            embed.add_field(
                name=f"{winner_name} - {date_str}",
                value=f"{type_emoji} **{entry['item']}** ({amount}pts)",
                inline=False
            )
        
        embed.set_footer(text=f"Showing {len(recent)} recent wins | Total: {len(winners)}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

