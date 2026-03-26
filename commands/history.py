import discord
import json
import datetime
from pathlib import Path



def load_loot_log():
    log = []
    if Path('loot_log.json').exists():
        with open('loot_log.json', 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        log.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    # Filter wins
    winners = [e for e in log if e['event'] in ['win', 'award', 'grant']]
    winners.sort(key=lambda x: x['timestamp'], reverse=True)
    return winners[:50]  # Recent 50

def setup(bot):
    @bot.tree.command(name="history", description="View recent winners history")
    @discord.app_commands.describe(limit="Number of recent entries to show (default 10, max 50)")
    async def history_cmd(interaction: discord.Interaction, limit: int = 10):
        if limit > 50:
            limit = 50
        
        history = load_loot_log()
        if not history:
            await interaction.response.send_message("📜 No winner history yet.")
            return
        
        recent = history[:limit]
        
        # Resolve user names
        unique_ids = {entry['user_id'] for entry in recent}
        winner_names = {}
        guild = interaction.guild
        for uid in unique_ids:
            member = guild.get_member(uid)
            winner_names[uid] = member.display_name if member else f"Unknown User ({uid})"
        
        embed = discord.Embed(
            title="🏆 Winner History",
            description="Recent winners with name, date, item, points",
            color=discord.Color.gold()
        )
        
        for entry in recent:
            timestamp = datetime.datetime.fromisoformat(entry["timestamp"])
            date_str = timestamp.strftime("%Y-%m-%d %H:%M")
            winner_name = winner_names[entry['user_id']]
            type_emoji = "✅" if entry["event"] == "win" else "🎁" if entry["event"] in ["award", "grant"] else "❓"
            amount = entry.get('amount', 0)
            embed.add_field(
                name=f"{winner_name} - {date_str}",
                value=f"{type_emoji} **{entry['item']}** ({amount} pts)",
                inline=False
            )
        
        embed.set_footer(text=f"Showing {len(recent)} most recent | Total wins: {len(history)}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
