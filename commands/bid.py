import datetime

import discord

from .loot import bid_aliases, claim_aliases, loot_meta, bids, loot_costs
from .logger import log_event
from .utils import can_spend, spend_points, add_points, get_points
from .loot import format_time_left


def setup(bot):
    @bot.tree.command(name="bid", description="Place a bid on an item")
    async def bid_cmd(interaction: discord.Interaction, code: str, amount: int):
        lookup = str(code).strip().lower()
        item = bid_aliases.get(lookup) or claim_aliases.get(lookup)
        if not item:
            await interaction.response.send_message("❌ Invalid bidding code. Use `/items` for list.")
            return
        if not loot_meta.get(item, {}).get("is_bidding", False):
            await interaction.response.send_message(f"❌ {item} cannot be bid on. Use `/claim {lookup}`.")
            return
        user_id = interaction.user.id

        if amount < 10:
            await interaction.response.send_message("❌ Minimum bid is 10 points.")
            return

        if not can_spend(user_id, amount, item, is_bid=True):
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

        from .utils import spend_points, add_points
        # Refund old bid first
        if current_bid > 0:
            add_points(user_id, current_bid)
            print(f"[BID] Refunded {current_bid} pts to {user_id}")

        # Deduct new bid
        spend_points(user_id, amount, item)
        bids[item]["players"][user_id] = amount
        log_event("bid", user_id, item, amount)

        embed = discord.Embed(title=f"🏆 Bids for {item}", color=discord.Color.gold())
        
        # Sort bids highest first
        sorted_bids = sorted(bids[item]["players"].items(), key=lambda x: x[1], reverse=True)
        bid_text = ""
        for i, (bid_user_id, bid_amt) in enumerate(sorted_bids[:5], 1):
            bidder = interaction.guild.get_member(bid_user_id)
            name = bidder.display_name if bidder else f"Unknown ({bid_user_id})"
            emoji = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "➤"
            bid_text += f"{emoji} **{name}**: {bid_amt} pts\n"
        
        if len(bids[item]["players"]) > 5:
            bid_text += f"... and {len(bids[item]['players'])-5} more"
        
        now = datetime.datetime.now()
        time_left = 86400 - (now - bids[item]["timestamp"]).total_seconds()
        timer = format_time_left(time_left)
        embed.add_field(name="Current Bids", value=bid_text or "No bids yet", inline=False)
        embed.add_field(name="⏰ Time Left", value=timer, inline=True)
        
        user_points = get_points(user_id)
        embed.set_footer(text=f"Your points: {user_points}")
        
        await interaction.response.send_message(embed=embed)
