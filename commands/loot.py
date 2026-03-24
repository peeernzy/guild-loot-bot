import discord, random, asyncio, datetime
from .utils import can_spend, spend_points, weekly_spent, remaining_claims, add_points
from .logger import log_event

claims = {}
bids = {}
leaderboard = {}

loot_costs = {
    "Rare Equipment": {"cost": 10, "rule": "No limit"},
    "Rare Weapon": {"cost": 5, "rule": "Bidding only, uncapped"},
    "Rare Materials": {"cost": 1, "rule": "Max 5 per member"},
    "Radiant Enchantment Stone": {"cost": 2, "rule": "Max 3 per member"},
    "Darkening Enchantment Stone": {"cost": 2, "rule": "Max 3 per member"},  # ✅ added
    "Middle Horn": {"cost": 3, "rule": "Max 1 per week"},
    "Lesser Horn": {"cost": 1, "rule": "Max 3 per week"},
    "Silvarin": {"cost": 1, "rule": "Max 5 per member"},  # ✅ added
    "Gwemix Piece Pouch": {"cost": 10, "rule": "Bidding only, uncapped"},
    "Artisan": {"cost": 10, "rule": "Bidding only, uncapped"},
}

loot_aliases = {
    "1": "Rare Equipment",
    "2": "Rare Weapon",
    "3": "Rare Materials",
    "4": "Radiant Enchantment Stone",
    "5": "Darkening Enchantment Stone",
    "6": "Middle Horn",
    "7": "Lesser Horn",
    "8": "Silvarin",
    "9": "Gwemix Piece Pouch",
    "10": "Artisan",
    "equip": "Rare Equipment",
    "weapon": "Rare Weapon",
    "mat": "Rare Materials",
    "radstone": "Radiant Enchantment Stone",
    "darkstone": "Darkening Enchantment Stone",
    "mhorn": "Middle Horn",
    "lhorn": "Lesser Horn",
    "silv": "Silvarin",
    "gwemix": "Gwemix Piece Pouch",
    "artisan": "Artisan"
}

CHANNEL_ID = 1485956297227763752  # 🔧 CHANGE THIS

# =========================
# BACKGROUND TASK
# =========================
async def check_claims(bot):
    await bot.wait_until_ready()

    while not bot.is_closed():
        now = datetime.datetime.now()
        channel = bot.get_channel(CHANNEL_ID)

        if not channel:
            await asyncio.sleep(60)
            continue

        # ===== FIXED CLAIMS =====
        for item, data in list(claims.items()):
            if (now - data["timestamp"]).total_seconds() >= 86400:
                if data["players"]:
                    winner_id = random.choice(data["players"])
                    guild = channel.guild
                    winner = await guild.fetch_member(winner_id)
                    cost = loot_costs.get(item, {"cost": 0})["cost"]

                    if not can_spend(winner_id, cost, item):
                        await channel.send(f"⚠️ {winner.display_name} cannot afford {item}.")
                        del claims[item]
                        continue

                    spend_points(winner_id, cost, item)
                    leaderboard[winner_id] = leaderboard.get(winner_id, 0) + 1
                    log_event("win", winner_id, item, cost)

                    await channel.send(f"🎉 {winner.display_name} won {item}! (-{cost} pts)")

                del claims[item]

        # ===== BIDDING =====
        for item, bid_data in list(bids.items()):
            if (now - bid_data["timestamp"]).total_seconds() >= 86400:
                if bid_data["players"]:
                    winner_id = max(bid_data["players"], key=bid_data["players"].get)
                    winning_bid = bid_data["players"][winner_id]

                    guild = channel.guild
                    winner = await guild.fetch_member(winner_id)

                    if can_spend(winner_id, winning_bid, item):
                        spend_points(winner_id, winning_bid, item)
                        leaderboard[winner_id] = leaderboard.get(winner_id, 0) + 1
                        log_event("win", winner_id, item, winning_bid)

                        await channel.send(
                            f"🎉 {winner.display_name} won {item} with {winning_bid} pts!"
                        )
                    else:
                        await channel.send(
                            f"⚠️ {winner.display_name} couldn’t afford their bid."
                        )

                del bids[item]

        await asyncio.sleep(60)

# =========================
# SETUP COMMANDS
# =========================
def setup(bot):

    # ===== CLAIM =====
    @bot.tree.command(name="claim", description="Claim loot")
    async def claim_cmd(interaction: discord.Interaction, code: str):
        if code not in loot_aliases:
            await interaction.response.send_message("❌ Invalid code.")
            return

        item = loot_aliases[code]
        user_id = interaction.user.id
        rule = loot_costs[item]["rule"]
        cost = loot_costs[item]["cost"]

        if rule.startswith("Bidding"):
            await interaction.response.send_message(f"❌ Use /bid for {item}.")
            return

        if not can_spend(user_id, cost, item):
            await interaction.response.send_message(f"❌ Not enough points.")
            return

        now = datetime.datetime.now()

        if item not in claims:
            claims[item] = {"players": [], "timestamp": now}

        # ✅ prevent spam duplicate
        if user_id not in claims[item]["players"]:
            claims[item]["players"].append(user_id)

        log_event("claim", user_id, item, cost)

        remaining = remaining_claims(user_id, item)
        msg = f"{interaction.user.display_name} claimed {item}!"

        if remaining is not None:
            msg += f"\n➡️ Remaining this week: {remaining}"

        await interaction.response.send_message(msg)

    # ===== BID =====
    @bot.tree.command(name="bid", description="Bid on loot")
    async def bid_cmd(interaction: discord.Interaction, code: str, amount: int):
        if code not in loot_aliases:
            await interaction.response.send_message("❌ Invalid code.")
            return

        item = loot_aliases[code]
        user_id = interaction.user.id
        min_cost = loot_costs[item]["cost"]
        rule = loot_costs[item]["rule"]

        if not rule.startswith("Bidding"):
            await interaction.response.send_message("❌ Not a bidding item.")
            return

        if amount < min_cost:
            await interaction.response.send_message(f"❌ Min bid is {min_cost}.")
            return

        if not can_spend(user_id, amount, item):
            await interaction.response.send_message("❌ Not enough points.")
            return

        now = datetime.datetime.now()

        if item not in bids:
            bids[item] = {"players": {}, "timestamp": now}

        current_bid = bids[item]["players"].get(user_id, 0)

        # ✅ prevent lowering bid
        if amount <= current_bid:
            await interaction.response.send_message(
                f"❌ Must bid higher than {current_bid}."
            )
            return

        bids[item]["players"][user_id] = amount
        log_event("bid", user_id, item, amount)

        await interaction.response.send_message(
            f"{interaction.user.display_name} bid {amount} on {item}!"
        )

    # ===== GRANT =====
    @bot.tree.command(name="grant", description="Grant loot")
    async def grant_cmd(interaction: discord.Interaction, member: discord.Member, code: str, cost: int = None):

        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        if code not in loot_aliases:
            await interaction.response.send_message("❌ Invalid code.", ephemeral=True)
            return

        item = loot_aliases[code]
        base_cost = loot_costs[item]["cost"]
        final_cost = cost if cost is not None else base_cost

        if not can_spend(member.id, final_cost, item):
            await interaction.response.send_message("❌ Cannot afford.", ephemeral=True)
            return

        spend_points(member.id, final_cost, item)
        leaderboard[member.id] = leaderboard.get(member.id, 0) + 1
        log_event("grant", member.id, item, final_cost)

        await interaction.response.send_message(
            f"✅ {member.display_name} got {item} (-{final_cost})"
        )

    # ===== REFUND =====
    @bot.tree.command(name="refund", description="Refund points")
    async def refund_cmd(interaction: discord.Interaction, member: discord.Member, amount: int):

        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        add_points(member.id, amount)
        log_event("refund", member.id, "Points", amount)

        await interaction.response.send_message(
            f"✅ Refunded {amount} to {member.display_name}"
        )

    
    # ===== START TASK =====
    @bot.event
    async def on_ready():
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands: {[cmd.name for cmd in synced]}")
        bot.loop.create_task(check_claims(bot))