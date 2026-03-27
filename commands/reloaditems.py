import discord
from discord import app_commands
from .loot import reload_loot_items, loot_meta, loot_costs, claim_aliases, bid_aliases

def setup(bot):
    @app_commands.describe()
    @bot.tree.command(name="reloaditems", description="Reload loot items from DB (sync command)")
    async def reloaditems_cmd(interaction: discord.Interaction):
        old_total = len(loot_meta)
        reload_loot_items()
        new_total = len(loot_meta)
        claim_count = sum(1 for name in loot_meta if not loot_meta[name].get("is_bidding", False))
        bid_count = new_total - claim_count
        
        embed = discord.Embed(title="🔄 Reload Complete", color=discord.Color.green())
        embed.add_field(
            name="📊 Items", 
            value=f"**Before:** `{old_total}` → **After:** `{new_total}`\n**Claim:** `{claim_count}` | **Bid:** `{bid_count}`", 
            inline=False
        )
        embed.add_field(name="✅ Updated", value=f"`loot_costs`: `{len(loot_costs)}`\n`claim_aliases`: `{len(claim_aliases)}`\n`bid_aliases`: `{len(bid_aliases)}`", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

