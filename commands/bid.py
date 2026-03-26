import datetime

import discord

from .loot import bid_aliases, claim_aliases, loot_meta, bids, loot_costs
from .logger import log_event
from .utils import can_spend


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
        spend_points(user_id, amount, item)  # Deduct on bid
        bids[item]["players"][user_id] = amount
        log_event("bid", user_id, item, amount)

        await interaction.response.send_message(
            f"{interaction.user.display_name} bid {amount} on {item}! (deducted)"
        )
