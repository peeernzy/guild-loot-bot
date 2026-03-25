import discord
import json
import datetime
from pathlib import Path

HISTORY_FILE = Path("winners_history.json")

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def append_winner(username: str, user_id: int, item: str, points: int, event_type: str):
    entry = {
        "username": username,
        "user_id": user_id,
        "item": item,
        "points": points,
        "type": event_type,
        "timestamp": datetime.datetime.now().isoformat()
    }
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, default=str)

def setup(bot):
    @bot.tree.command(name="history", description="View recent winners history")
    @discord.app_commands.describe(limit="Number of recent entries to show (default 10, max 50)")
    async def history_cmd(interaction: discord.Interaction, limit: int = 10):
        if limit > 50:
            limit = 50
        
        history = load_history()
        if not history:
            await interaction.response.send_message("📜 No winner history yet.")
            return
        
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        recent = history[:limit]
        
        embed = discord.Embed(
            title="🏆 Winner History",
            description="Recent claim/bid/award winners",
            color=discord.Color.gold()
        )
        
        for entry in recent:
            timestamp = datetime.datetime.fromisoformat(entry["timestamp"])
            date_str = timestamp.strftime("%Y-%m-%d %H:%M")
            type_emoji = "✅" if entry["type"] in ["claim", "claim_win"] else "⚔️" if "bid" in entry["type"] else "🎁"
            value = f"{type_emoji} **{entry['username']}** won **{entry['item']}** (-{entry['points']} pts)"
            embed.add_field(
                name=date_str,
                value=value,
                inline=False
            )
        
        embed.set_footer(text=f"Showing {len(recent)} most recent | Total: {len(history)}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

