import discord, asyncio, datetime, json
from .utils import can_spend, spend_points, weekly_spent, remaining_claims, add_points
from .logger import log_event

claims = {}
bids = {}
leaderboard = {}

# Load loot items from JSON file
def load_loot_items():
    try:
        with open("loot_items.json", "r") as f:
            data = json.load(f)
            items = data.get("items", [])
            
            # Build loot_costs dict
            costs = {}
            for item in items:
                costs[item["name"]] = {
                    "cost": item["cost"],
                    "rule": item["rule"]
                }
            
            # Build loot_aliases dict
            aliases = {}
            for item in items:
                aliases[item["code"]] = item["name"]
                for alias in item.get("aliases", []):
                    aliases[alias] = item["name"]
            
            return costs, aliases
    except FileNotFoundError:
        print("❌ loot_items.json not found. Using fallback defaults.")
        return {}, {}

loot_costs, loot_aliases = load_loot_items()

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
        rule = loot_costs[item]["rule"]

        if not rule.startswith("Bidding"):
            await interaction.response.send_message("❌ Not a bidding item.")
            return

        # Minimum bid is always 10 points
        if amount < 10:
            await interaction.response.send_message(f"❌ Minimum bid is 10 points.")
            return

        if not can_spend(user_id, amount, item):
            await interaction.response.send_message("❌ Not enough points.")
            return

        now = datetime.datetime.now()

        if item not in bids:
            bids[item] = {"players": {}, "timestamp": now}

        current_bid = bids[item]["players"].get(user_id, 0)
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

    # ===== VIEW CLAIMS LEADERBOARD =====
    @bot.tree.command(name="claimsleaderboard", description="View all current item claims")
    async def claims_leaderboard_cmd(interaction: discord.Interaction):
        if not claims:
            await interaction.response.send_message("📋 No active claims.")
            return

        embed = discord.Embed(
            title="📋 Current Claims",
            description="Items waiting for manual distribution",
            color=discord.Color.blue()
        )

        for item, data in sorted(claims.items()):
            player_list = []
            for player_id in data["players"]:
                member = interaction.guild.get_member(player_id)
                if member:
                    player_list.append(f"• {member.display_name}")
            
            if player_list:
                cost = loot_costs.get(item, {}).get("cost", 0)
                embed.add_field(
                    name=f"{item} ({cost} pts)",
                    value="\n".join(player_list),
                    inline=False
                )

        await interaction.response.send_message(embed=embed)

    # ===== VIEW BIDS LEADERBOARD =====
    @bot.tree.command(name="bidsleaderboard", description="View all current bids")
    async def bids_leaderboard_cmd(interaction: discord.Interaction):
        if not bids:
            await interaction.response.send_message("🏆 No active bids.")
            return

        embed = discord.Embed(
            title="🏆 Current Bids",
            description="Bidding items with highest bids",
            color=discord.Color.gold()
        )

        for item, bid_data in sorted(bids.items()):
            if bid_data["players"]:
                # Get highest bid
                highest_bidder_id = max(bid_data["players"], key=bid_data["players"].get)
                highest_member = interaction.guild.get_member(highest_bidder_id)
                highest_bid = bid_data["players"][highest_bidder_id]
                
                bid_list = []
                for player_id, amount in sorted(bid_data["players"].items(), key=lambda x: x[1], reverse=True):
                    member = interaction.guild.get_member(player_id)
                    if member:
                        marker = "👑" if player_id == highest_bidder_id else "  "
                        bid_list.append(f"{marker} {member.display_name}: {amount} pts")
                
                embed.add_field(
                    name=f"{item}",
                    value="\n".join(bid_list),
                    inline=False
                )

        await interaction.response.send_message(embed=embed)

    # ===== END BIDDING (AUTO-SELECT HIGHEST BIDDER) =====
    @bot.tree.command(name="endbidding", description="Moderator-only: End bidding and announce winner (auto-select highest bidder)")
    async def end_bidding_cmd(interaction: discord.Interaction, item: str):
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        # Find the item
        target_item = None
        for alias, item_name in loot_aliases.items():
            if item.lower() == item_name.lower() or item.lower() == alias.lower():
                target_item = item_name
                break

        if not target_item or target_item not in bids:
            await interaction.response.send_message(
                f"❌ Item '{item}' not found in active bids.\nUse `/bidsleaderboard` to see options.",
                ephemeral=True
            )
            return

        # Get highest bidder
        if not bids[target_item]["players"]:
            await interaction.response.send_message(
                f"❌ No bids on {target_item}.",
                ephemeral=True
            )
            return

        winner_id = max(bids[target_item]["players"], key=bids[target_item]["players"].get)
        winning_bid = bids[target_item]["players"][winner_id]
        winner = interaction.guild.get_member(winner_id)

        # Award the bid
        if not can_spend(winner_id, winning_bid, target_item):
            await interaction.response.send_message(
                f"❌ {winner.display_name} cannot afford their bid ({winning_bid} pts).",
                ephemeral=True
            )
            return

        spend_points(winner_id, winning_bid, target_item)
        leaderboard[winner_id] = leaderboard.get(winner_id, 0) + 1
        log_event("win", winner_id, target_item, winning_bid)

        # Remove from bids
        del bids[target_item]

        # Announce to channel
        channel = interaction.guild.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(
                f"🎉 **Bidding Ended!**\n{winner.display_name} won **{target_item}** with a bid of {winning_bid} pts!"
            )

        await interaction.response.send_message(
            f"✅ Bidding ended. {winner.display_name} won {target_item}!",
            ephemeral=True
        )

    # ===== AWARD (MANUAL DISTRIBUTION) =====
    @bot.tree.command(name="award", description="Moderator-only: Manually award item to a claimer")
    async def award_cmd(interaction: discord.Interaction, item: str, member: discord.Member):
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        # Find the item (by name or code)
        target_item = None
        for alias, item_name in loot_aliases.items():
            if item.lower() == item_name.lower() or item.lower() == alias.lower():
                target_item = item_name
                break

        if not target_item or target_item not in claims:
            await interaction.response.send_message(
                f"❌ Item '{item}' not found in active claims.\nUse `/claimsleaderboard` to see options.",
                ephemeral=True
            )
            return

        # Check if member claimed this item
        if member.id not in claims[target_item]["players"]:
            await interaction.response.send_message(
                f"❌ {member.display_name} did not claim {target_item}.",
                ephemeral=True
            )
            return

        # Award the item
        cost = loot_costs.get(target_item, {"cost": 0})["cost"]

        if not can_spend(member.id, cost, target_item):
            await interaction.response.send_message(
                f"❌ {member.display_name} cannot afford {target_item}.",
                ephemeral=True
            )
            return

        spend_points(member.id, cost, target_item)
        leaderboard[member.id] = leaderboard.get(member.id, 0) + 1
        log_event("award", member.id, target_item, cost)

        # Remove from claims
        claims[target_item]["players"].remove(member.id)
        if not claims[target_item]["players"]:
            del claims[target_item]

        await interaction.response.send_message(
            f"✅ {member.display_name} awarded **{target_item}** (-{cost} pts)"
        )

    # ===== CLEAR EXPIRED CLAIMS =====
    @bot.tree.command(name="clearclaims", description="Moderator-only: Clear expired claims (older than 7 days)")
    async def clear_claims_cmd(interaction: discord.Interaction):
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        now = datetime.datetime.now()
        cleared = []

        for item, data in list(claims.items()):
            age_days = (now - data["timestamp"]).total_seconds() / 86400
            if age_days > 7:
                cleared.append(f"{item} ({int(age_days)} days old)")
                del claims[item]

        if cleared:
            await interaction.response.send_message(
                f"✅ Cleared {len(cleared)} expired claims:\n" + "\n".join(cleared),
                ephemeral=True
            )
        else:
            await interaction.response.send_message("✅ No expired claims to clear.", ephemeral=True)

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