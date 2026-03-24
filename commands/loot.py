import discord, random, asyncio, datetime
from .utils import can_spend, spend_points, weekly_spent

claims = {}
leaderboard = {}

loot_costs = {
    "Rare Equipment": {"cost": 10, "rule": "No limit"},
    "Rare Weapon": {"cost": 5, "rule": "Bidding only, uncapped"},
    "Radiant Enchantment Stone": {"cost": 2, "rule": "Max 3 per member"},
    "Middle Horn": {"cost": 3, "rule": "Max 1 per week"},
    "Lesser Horn": {"cost": 1, "rule": "Max 1 per week"},
    # add others...
}

async def check_claims(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.datetime.now()
        for item, data in list(claims.items()):
            if (now - data["timestamp"]).total_seconds() >= 86400:
                if data["players"]:
                    winner_id = random.choice(data["players"])
                    guild = bot.guilds[0]
                    winner = await guild.fetch_member(winner_id)
                    channel = guild.text_channels[0]
                    cost = loot_costs.get(item, {"cost": 0})["cost"]

                    if not can_spend(winner_id, cost):
                        await channel.send(f"⚠️ {winner.display_name} hit weekly cap.")
                        continue
                    spend_points(winner_id, cost)

                    leaderboard[winner_id] = leaderboard.get(winner_id, 0) + 1
                    await channel.send(f"🎉 {winner.display_name} won {item}! Deducted {cost} points.")
                del claims[item]
        await asyncio.sleep(60)

def setup(bot):
    @bot.tree.command(name="claim", description="Claim loot items")
    async def claim_cmd(interaction: discord.Interaction, item: str):
        user_id = interaction.user.id
        now = datetime.datetime.now()
        if item not in claims:
            claims[item] = {"players": [], "timestamp": now}
        claims[item]["players"].append(user_id)
        await interaction.response.send_message(f"{interaction.user.display_name} claimed {item}! Spin in 24h.")

    # Instead of bot.loop, use setup_hook
    async def start_tasks():
        bot.loop.create_task(check_claims(bot))

    bot.setup_hook = start_tasks
