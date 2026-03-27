import discord
import discord
from discord import app_commands
from .loot import claim_aliases, bid_aliases, loot_costs, loot_meta
from .utils import get_points, remaining_claims

def setup(bot):
    @discord.app_commands.describe(filter="common/uncommon/rare/legendary/points/all")
    @bot.tree.command(name="items", description="Show loot items by rarity or filter")
    async def items_cmd(interaction: discord.Interaction, filter: str = "all"):
        user_pts = get_points(interaction.user.id)
        filter = filter.lower().strip()

        embed = discord.Embed(title="🎁 Loot Shop", color=discord.Color.gold())
        
        claim_items = []
        bid_items = []

        # Filter logic
        for name in loot_meta:
            rarity = loot_meta[name].get("rarity", "common")
            cost = loot_costs[name]["cost"]
            rule = loot_costs[name]["rule"]
            
            # Apply filters
            if filter != "all":
                if filter == "points" and cost > user_pts:
                    continue
                if filter == rarity:
                    pass
                else:
                    continue
            
            is_bidding = loot_meta[name]["is_bidding"]
            remaining = remaining_claims(interaction.user.id, name)
            extra = f"\n📊 Rem: {remaining}" if remaining is not None else ""
            
            stock = loot_meta[name]["stock"]
            stock_text = f"**Stock:** {stock}" if stock < 999 else "**Stock:** Unlimited"
            
            aliases = loot_meta[name]["aliases"]
            alias = aliases[0] if aliases else loot_meta[name]["source_code"]
            field_name = f"{get_emoji(name, rarity)} [`{alias}`] {name}"
            field_value = f"**Cost:** {cost} pts\n{stock_text}\n**Rule:** {rule}\n**Rarity:** {rarity.title()}{extra}"
            
            if is_bidding:
                bid_items.append((cost, field_name, field_value))
            else:
                claim_items.append((cost, field_name, field_value))

        # Sort & add claim items
        for cost, name, value in sorted(claim_items):
            embed.add_field(name=name, value=value, inline=True)
        
        # Sort & add bid items (high→low)
        if bid_items:
            embed.add_field(name="⚔️ BIDDING ITEMS", value="Use `/bid [alias] [pts]`", inline=False)
            for cost, name, value in sorted(bid_items, reverse=True):
                embed.add_field(name=name, value=value, inline=True)

        if not claim_items and not bid_items:
            embed.description = f"**No {filter} items found.**\nTry: common, uncommon, rare, legendary, points, all"
        else:
            embed.description = f"💰 **Your Points: {user_pts}**\n*Filter: {filter or 'all'}*"
        
        embed.set_footer(text="/points | /restock | /stock")

        await interaction.response.send_message(embed=embed, ephemeral=True)

def get_emoji(name: str, rarity: str) -> str:
    """Emoji by rarity/name"""
    emojis = {
        "common": "⚪",
        "uncommon": "🟢", 
        "rare": "🔵",
        "legendary": "🟣"
    }
    return emojis.get(rarity, "❔")
