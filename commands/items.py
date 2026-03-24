import discord
from .loot import loot_costs

def setup(bot):
    @bot.tree.command(name="items", description="Show list of loot items, costs, and rules")
    async def items_cmd(interaction: discord.Interaction):
        item_list = "\n".join([
            f"{item}: {data['cost']} points ({data['rule']})"
            for item, data in loot_costs.items()
        ])
        await interaction.response.send_message(f"📜 Loot Items & Rules:\n{item_list}")
