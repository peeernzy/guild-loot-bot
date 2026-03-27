import discord
from discord import app_commands
from .loot import claim_aliases, bid_aliases, loot_costs, loot_meta
from .utils import get_points, remaining_claims

def setup(bot):
    @app_commands.describe(filter="common/uncommon/rare/legendary/points/all")
    @bot.tree.command(name="items", description="Show loot items by rarity or filter (fancy view)")
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
        
        embed.set_footer(text="`/itemlist` plain table | /points | /restock")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="itemlist", description="Simple table of all loot items (code, name, cost, rule, stock, rarity)")
    async def itemlist_cmd(interaction: discord.Interaction):
        embed = discord.Embed(title="📋 Loot Items Masterlist", color=discord.Color.blurple())
        
        claim_table = "```\nCODE  | NAME             | COST | RULE   | STOCK | RARITY\n"
        bid_table = "```\nCODE  | NAME             | COST | RULE   | STOCK | RARITY\n"
        
        claim_count = 0
        bid_count = 0

        for name in sorted(loot_meta):
            code = loot_meta[name]["source_code"]
            cost = loot_costs[name]["cost"]
            rule = loot_costs[name]["rule"][:6]  # Shorten rule
            stock = loot_meta[name]["stock"]
            rarity = loot_meta[name]["rarity"][:5]  # Shorten rarity
            
            row = f"{code:4} | {name[:15]:15} | {cost:4} | {rule:6} | {stock:5} | {rarity}"
            
            if loot_meta[name]["is_bidding"]:
                bid_table += row + "\n"
                bid_count += 1
            else:
                claim_table += row + "\n"
                claim_count += 1

        claim_table += "```"
        bid_table += "```"

        embed.add_field(name=f"✅ Claim Items ({claim_count})", value=claim_table, inline=False)
        if bid_count > 0:
            embed.add_field(name=f"⚔️ Bid Items ({bid_count})", value=bid_table, inline=False)

        embed.set_footer(text="Use `/items` for fancy view with emojis/stock info")
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
