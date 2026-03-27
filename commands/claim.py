import datetime

import discord

from .loot import claim_aliases, bid_aliases, loot_meta, claims, loot_costs
from .logger import log_event
from .utils import can_spend, remaining_claims, add_points, spend_points, get_points

def setup(bot):
    @bot.tree.command(name="claim", description="Claim a loot item")
    async def claim_cmd(interaction: discord.Interaction, code: str):
        lookup = str(code).strip().lower()
        item = claim_aliases.get(lookup) or bid_aliases.get(lookup)
        if not item:
            await interaction.response.send_message("❌ Invalid code. Use `/items` for list.")
            return
        if loot_meta.get(item, {}).get("is_bidding", False):
            await interaction.response.send_message(f"❌ {item} is bidding-only. Use `/bid {lookup}`.")
            return
        stock = loot_meta.get(item, {}).get("stock", 999)
        if stock <= 0:
            await interaction.response.send_message(f"❌ **{item}** sold out (0 stock left).")
            return
        user_id = interaction.user.id
        cost = loot_costs[item]["cost"]

        if not can_spend(user_id, cost, item):
            await interaction.response.send_message("❌ Not enough points.")
            return

        now = datetime.datetime.now()

        if item not in claims:
            claims[item] = {"players": [], "timestamp": now}

        if user_id not in claims[item]["players"]:
            claims[item]["players"].append(user_id)
            spend_points(user_id, cost, item)
            log_event("claim", user_id, item, cost)

            remaining = remaining_claims(user_id, item)
            msg = f"{interaction.user.display_name} claimed {item}! (-{cost} pts)"
            if remaining is not None:
                msg += f"\n➡️ Remaining this week: {remaining}"

            await interaction.response.send_message(msg)

    @bot.tree.command(name="claimcancel", description="Cancel your claim on an item (refund points)")
    async def claimcancel_cmd(interaction: discord.Interaction, code: str):
        lookup = str(code).strip().lower()
        item = claim_aliases.get(lookup) or bid_aliases.get(lookup)
        if not item:
            await interaction.response.send_message("❌ Invalid code. Use `/items` for list.", ephemeral=True)
            return
        if loot_meta.get(item, {}).get("is_bidding", False):
            await interaction.response.send_message(f"❌ {item} is bidding-only.", ephemeral=True)
            return
        user_id = interaction.user.id
        if item not in claims or user_id not in claims[item]["players"]:
            await interaction.response.send_message(f"❌ No active claim on {item}.", ephemeral=True)
            return
        cost = loot_costs.get(item, {}).get("cost", 0)
        add_points(user_id, cost)
        claims[item]["players"].remove(user_id)
        if not claims[item]["players"]:
            del claims[item]
        log_event("cancel_claim", user_id, item, cost)
        print(f"[CANCELCLAIM] Refunded {cost} pts to {user_id} for {item}")
        remaining_players = len(claims.get(item, {'players': []})['players']) if item in claims else 0
        await interaction.response.send_message(f"✅ Claim on **{item}** cancelled! **+{cost} pts** refunded.\nPlayers left: {remaining_players}", ephemeral=True)
