import discord
import json
from discord import app_commands
from .loot import claim_aliases, bid_aliases, loot_costs, loot_meta
from .utils import get_points, remaining_claims

def truncate_table(lines: list[str], header_title: str, max_len: int = 1010) -> str:
    """Build code block table with custom header, truncating to fit max_len chars."""
    if not lines:
        return ""
    
    header = f"```\n{header_title}\n"
    footer = "\n```"
    reserve = len(header) + len(footer) + 30  # buffer for truncation text
    available = max_len - reserve
    
    table_lines = []
    current_len = 0
    line_idx = 0
    
    while line_idx < len(lines):
        line = lines[line_idx]
        test_len = current_len + len(line) + 1  # +"\n"
        if test_len > available and table_lines:
            break
        table_lines.append(line)
        current_len = test_len
        line_idx += 1
    
    result = header + "\n".join(table_lines)
    if line_idx < len(lines):
        truncated_count = len(lines) - line_idx
        result += f"\n... +{truncated_count} more"
    result += footer
    return result

def setup(bot):
    @app_commands.describe(filter="common/uncommon/rare/epic/legend/mythic/points/all")
    @bot.tree.command
    async def items_cmd(interaction: discord.Interaction, filter: str = "all"):
        user_pts = get_points(interaction.user.id)
        filter = filter.lower().strip()

        embed = discord.Embed(title="🎁 Loot Shop", color=discord.Color.gold())
        
        claim_lines = []
        bid_lines = []

        for name in sorted(loot_meta):
            rarity = loot_meta[name].get("rarity", "common")
            
            # Filter
            if filter != "all" and filter != "points":
                if rarity != filter:
                    continue
            elif filter == "points":
                if loot_costs.get(name, {}).get("cost", 0) > user_pts:
                    continue
            
            cost = loot_costs.get(name, {}).get("cost", 0)
            stock = loot_meta[name].get("stock", 999)
            is_bidding = loot_meta[name].get("is_bidding", False)
            emoji = get_emoji(name, rarity)
            alias = loot_meta[name].get("aliases", []) 
            alias = alias[0] if alias else loot_meta[name].get("source_code", name)
            
            line = f"{emoji} **{alias}** ({name}) | {cost}p | S:{stock}"

            if is_bidding:
                bid_lines.append(line)
            else:
                claim_lines.append(line)


        # Claim table - dynamically truncate
        claim_table = truncate_table(claim_lines, "CLAIM ITEMS")
        if claim_table.strip():
            embed.add_field(name="✅ Claim", value=claim_table, inline=False)

        # Bid table - dynamically truncate
        bid_table = truncate_table(bid_lines, "BID ITEMS ( /bid [alias] [pts] )")
        if bid_table.strip():
            embed.add_field(name="⚔️ Bid", value=bid_table, inline=False)

        embed.description = f"💰 **Your Points: {user_pts}** | Filter: {filter}"
        embed.set_footer(text="`/itemlist` table | `/checkitemstore` | `/points` | `/restock` | `/impitems`")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="checkitemstore", description="Check item store count (DB)")
    async def checkitemstore_cmd(interaction: discord.Interaction):
        total_items = len(loot_meta)
        claim_count = sum(1 for name in loot_meta if not loot_meta[name].get("is_bidding", False))
        bid_count = total_items - claim_count
        
        embed = discord.Embed(title="🛒 Item Store Check (DB)", color=discord.Color.green())
        embed.add_field(
            name="📊 Counts", 
            value=f"**DB Loaded:** `{total_items}`\n**Claim:** `{claim_count}` **Bid:** `{bid_count}`", 
            inline=False
        )
        embed.add_field(
            name="Status", 
            value=f"loot_costs: `{len(loot_costs)}`", 
            inline=True
        )
        embed.add_field(
            name="Commands", 
            value="`/items` | `/itemlist`", 
            inline=True
        )
        embed.set_footer(text="Reload: `/reloaditems` | Import: `/impitems`")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="itemlist", description="Loot table (no rule column)")
    async def itemlist_cmd(interaction: discord.Interaction):
        embed = discord.Embed(title="📋 Loot Masterlist", color=discord.Color.blurple())
        
        claim_lines = []
        bid_lines = []

        for name in sorted(loot_meta):
            code = loot_meta[name].get("source_code", "N/A")
            cost = loot_costs.get(name, {}).get("cost", 0)
            stock = loot_meta[name].get("stock", 999)
            rarity = loot_meta[name].get("rarity", "unknown")[:6]
            is_bidding = loot_meta[name].get("is_bidding", False)
            
            line = f"`{code}` **{name[:18]}** | {cost}pts | Stock:{stock} | {rarity}"
            
            if is_bidding:
                bid_lines.append(line)
            else:
                claim_lines.append(line)

        if claim_lines:
            claim_table = truncate_table(claim_lines, "CLAIM | CODE | NAME | COST | STOCK | RARITY")
            embed.add_field(name=f"✅ Claim ({len(claim_lines)})", value=claim_table, inline=False)
        
        if bid_lines:
            bid_table = truncate_table(bid_lines, "BID | CODE | NAME | COST | STOCK | RARITY")
            embed.add_field(name=f"⚔️ Bid ({len(bid_lines)})", value=bid_table, inline=False)
        
        embed.set_footer(text="`/items` fancy | `/checkitemstore` | `/impitems` CSV | `/expitems` export")
        await interaction.response.send_message(embed=embed, ephemeral=True)

def get_emoji(name: str, rarity: str) -> str:
    emojis = {
        "common": "⚪",
        "uncommon": "🟢", 
        "rare": "🔵",
        "epic": "🔴",
        "legend": "🟡",
        "mythic": "🟣"
    }
    return emojis.get(rarity, "❓")

