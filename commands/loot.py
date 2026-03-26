import discord, asyncio, datetime, json, random
import os
from .utils import can_spend, spend_points, remaining_claims
from .logger import log_event

claims = {}
bids = {}
leaderboard = {}

def format_time_left(seconds: float) -> str:
    if seconds <= 0:
        return "Expired"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}h:{m:02d}m:{s:02d}s"

# Load loot items
def load_loot_items():
    try:
        with open("loot_items.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data.get("items", [])

            costs = {}
            claim_aliases = {}
            bid_aliases = {}
            item_meta = {}

            claim_index = 1
            bid_index = 1

            for item in items:
                name = item["name"]
                rule = item["rule"]
                normalized_aliases = [str(alias).strip().lower() for alias in item.get("aliases", []) if str(alias).strip()]

                costs[name] = {"cost": item["cost"], "rule": rule}

                is_bidding = str(rule).startswith("Bidding")
                scoped_code = str(bid_index if is_bidding else claim_index)

                item_meta[name] = {
                    "source_code": str(item["code"]),
                    "scoped_code": scoped_code,
                    "aliases": normalized_aliases,
                    "is_bidding": is_bidding,
                }

                target_aliases = bid_aliases if is_bidding else claim_aliases
                target_aliases[scoped_code] = name
                for alias in normalized_aliases:
                    target_aliases[alias] = name

                if is_bidding:
                    bid_index += 1
                else:
                    claim_index += 1

            return costs, claim_aliases, bid_aliases, item_meta
    except FileNotFoundError:
        print("❌ loot_items.json not found.")
        return {}, {}, {}, {}

loot_costs, claim_aliases, bid_aliases, loot_meta = load_loot_items()

def reload_loot_items():
    global loot_costs, claim_aliases, bid_aliases, loot_meta
    new_costs, new_claim_aliases, new_bid_aliases, new_meta = load_loot_items()
    loot_costs.clear()
    loot_costs.update(new_costs)
    claim_aliases.clear()
    claim_aliases.update(new_claim_aliases)
    bid_aliases.clear()
    bid_aliases.update(new_bid_aliases)
    loot_meta.clear()
    loot_meta.update(new_meta)

CHANNEL_ID = int(os.getenv('LOOT_CHANNEL_ID', '1485956297227763752'))

async def check_claims(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.datetime.now()
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            await asyncio.sleep(60)
            continue

        # Claims
        for item, data in list(claims.items()):
            if (now - data["timestamp"]).total_seconds() >= 86400:
                if data["players"]:
                    winner_id = random.choice(data["players"])
                    winner = await channel.guild.fetch_member(winner_id)
                    cost = loot_costs.get(item, {"cost": 0})["cost"]

                    if not can_spend(winner_id, cost, item):
                        await channel.send(f"⚠️ {winner.display_name} cannot afford {item}.")
                    else:
                        spend_points(winner_id, cost, item)
                        leaderboard[winner_id] = leaderboard.get(winner_id, 0) + 1
                        log_event("win", winner_id, item, cost)
                        await channel.send(f"🎉 {winner.display_name} won {item}! (-{cost} pts)")
                del claims[item]

        # Bids
        for item, bid_data in list(bids.items()):
            if (now - bid_data["timestamp"]).total_seconds() >= 86400:
                if bid_data["players"]:
                    top_bid = max(bid_data["players"].values())
                    top_bidders = [pid for pid, amt in bid_data["players"].items() if amt == top_bid]
                    winner_id = random.choice(top_bidders)
                    winning_bid = bid_data["players"][winner_id]
                    winner = await channel.guild.fetch_member(winner_id)

                    # Refund all losers
                    from .utils import add_points
                    for loser_id in bid_data["players"]:
                        if loser_id != winner_id:
                            loser_bid = bid_data["players"][loser_id]
                            add_points(loser_id, loser_bid)

                    # Winner already deducted - no extra deduct
                    leaderboard[winner_id] = leaderboard.get(winner_id, 0) + 1
                    log_event("win", winner_id, item, winning_bid)
                    await channel.send(f"🎉 {winner.display_name} won {item} with {winning_bid} pts!")
                    del bids[item]
                del bids[item]

        await asyncio.sleep(60)

def setup(bot):

    @bot.tree.command(name="claimsleaderboard", description="View active item claims")
    async def claims_leaderboard_cmd(interaction: discord.Interaction):
        if not claims:
            await interaction.response.send_message("📋 No active claims.")
            return

        embed = discord.Embed(title="📋 Current Claims", description="Items waiting for manual distribution", color=discord.Color.blue())
        now = datetime.datetime.now()
        for item, data in sorted(claims.items()):
            player_list = [interaction.guild.get_member(pid).display_name for pid in data["players"] if interaction.guild.get_member(pid)]
            if player_list:
                cost = loot_costs.get(item, {}).get("cost", 0)
                time_left = 86400 - (now - data["timestamp"]).total_seconds()
                embed.add_field(
                    name=f"{item} ({cost} pts)",
                    value="\n".join(f"• {name}" for name in player_list) + f"\n\n⏰ {format_time_left(time_left)}",
                    inline=False
                )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="bidsleaderboard", description="View active bids")
    async def bids_leaderboard_cmd(interaction: discord.Interaction):
        if not bids:
            await interaction.response.send_message("🏆 No active bids.")
            return

        embed = discord.Embed(title="🏆 Current Bids", description="Bidding items with highest bids", color=discord.Color.gold())
        now = datetime.datetime.now()
        for item, bid_data in sorted(bids.items()):
            if bid_data["players"]:
                highest_bidder_id = max(bid_data["players"], key=bid_data["players"].get)
                highest_bid = bid_data["players"][highest_bidder_id]
                bid_list = []
                for player_id, amount in sorted(bid_data["players"].items(), key=lambda x: x[1], reverse=True):
                    member = interaction.guild.get_member(player_id)
                    if member:
                        marker = "👑" if player_id == highest_bidder_id else "  "
                        bid_list.append(f"{marker} {member.display_name}: {amount} pts")
                time_left = 86400 - (now - bid_data["timestamp"]).total_seconds()
                embed.add_field(
                    name=f"{item}",
                    value="\n".join(bid_list) + f"\n\n⏰ {format_time_left(time_left)}",
                    inline=False
                )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="endbid", description="Close bidding for an item")
    async def end_bidding_cmd(interaction: discord.Interaction, item: str):
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        target_item = None
        item_lookup = item.lower()
        for alias_map in (bid_aliases, claim_aliases):
            for alias, item_name in alias_map.items():
                if item_lookup == item_name.lower() or item_lookup == alias.lower():
                    target_item = item_name
                    break
            if target_item:
                break

        if not target_item or target_item not in bids:
            await interaction.response.send_message(f"❌ Item '{item}' not found in active bids. Use `/bidsleaderboard`.", ephemeral=True)
            return

        if not bids[target_item]["players"]:
            await interaction.response.send_message(f"❌ No bids on {target_item}.", ephemeral=True)
            return

        winner_id = max(bids[target_item]["players"], key=bids[target_item]["players"].get)
        winning_bid = bids[target_item]["players"][winner_id]
        winner = interaction.guild.get_member(winner_id)

        # Already deducted on bid - skip spend_points & can_spend
        from .utils import add_points
        for loser_id in bids[target_item]["players"]:
            if loser_id != winner_id:
                loser_bid = bids[target_item]["players"][loser_id]
                add_points(loser_id, loser_bid)
        
        leaderboard[winner_id] = leaderboard.get(winner_id, 0) + 1
        log_event("win", winner_id, target_item, winning_bid)
        del bids[target_item]

        channel = interaction.guild.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"🎉 **Bidding Ended!** {winner.display_name} won **{target_item}** with {winning_bid} pts!")

        await interaction.response.send_message(f"✅ Bidding ended. {winner.display_name} won {target_item}!", ephemeral=True)

    @bot.tree.command(name="award", description="Award an item to a member")
    async def award_cmd(interaction: discord.Interaction, item: str, member: discord.Member):
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        target_item = None
        item_lookup = item.lower()
        for alias_map in (claim_aliases, bid_aliases):
            for alias, item_name in alias_map.items():
                if item_lookup == item_name.lower() or item_lookup == alias.lower():
                    target_item = item_name
                    break
            if target_item:
                break

        if not target_item or target_item not in claims:
            await interaction.response.send_message(f"❌ Item '{item}' not found in active claims. Use `/claimsleaderboard`.", ephemeral=True)
            return

        if member.id not in claims[target_item]["players"]:
            await interaction.response.send_message(f"❌ {member.display_name} did not claim {target_item}.", ephemeral=True)
            return

        cost = loot_costs.get(target_item, {"cost": 0})["cost"]

        if not can_spend(member.id, cost, target_item):
            await interaction.response.send_message(f"❌ {member.display_name} cannot afford {target_item}.", ephemeral=True)
            return

        spend_points(member.id, cost, target_item)
        leaderboard[member.id] = leaderboard.get(member.id, 0) + 1
        log_event("award", member.id, target_item, cost)

        claims[target_item]["players"].remove(member.id)
        if not claims[target_item]["players"]:
            del claims[target_item]

        await interaction.response.send_message(f"✅ {member.display_name} awarded **{target_item}** (-{cost} pts)")

    @bot.tree.command(name="clearclaims", description="Clear expired claims")
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
            await interaction.response.send_message(f"✅ Cleared {len(cleared)} expired claims:\n" + "\n".join(cleared), ephemeral=True)
        else:
            await interaction.response.send_message("✅ No expired claims to clear.", ephemeral=True)

    @bot.event
    async def on_ready():
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands: {[cmd.name for cmd in synced]}")
        bot.loop.create_task(check_claims(bot))
