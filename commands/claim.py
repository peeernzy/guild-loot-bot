import datetime

import discord

from .loot import claim_aliases, claims, loot_costs
from .logger import log_event
from .utils import can_spend, remaining_claims


def setup(bot):
    @bot.tree.command(name="claim", description="Claim a loot item")
    async def claim_cmd(interaction: discord.Interaction, code: str):
        lookup = str(code).strip().lower()
        if lookup not in claim_aliases:
            await interaction.response.send_message("❌ Invalid claim code.")
            return

        item = claim_aliases[lookup]
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

        log_event("claim", user_id, item, cost)

        remaining = remaining_claims(user_id, item)
        msg = f"{interaction.user.display_name} claimed {item}!"
        if remaining is not None:
            msg += f"\n➡️ Remaining this week: {remaining}"

        await interaction.response.send_message(msg)
