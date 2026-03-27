import discord
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
    @app_commands.describe(filter="common/uncommon/rare/legendary/points/all")
    @bot.tree.command(name="items", description="Loot shop - fancy view by filter")
    async def items_cmd(interaction: discord.Interaction, filter: str = "all"):
        user_pts = get_points(interaction.user.id)
        filter = filter.lower().strip()

        embed = discord.Embed(title="🎁 Loot Shop", color=discord.Color.gold())
        
        claim_lines = []
        bid_lines = []

        for name in sorted(loot_meta):
            rarity = loot_meta[name].get("rarity", "common")
            
            # Filter
            if filter != "all":
                if filter == "points" and loot_costs[name]["cost"] > user_pts:
                    continue
                if rarity != filter:
                    continue
            
            cost = loot_costs[name]["cost"]
            rule = loot_costs[name]["rule"]
            stock = loot_meta[name]["stock"]
            is_bidding = loot_meta[name]["is_bidding"]
            remaining = remaining_claims(interaction.user.id, name)
            
            emoji = get_emoji(name, rarity)
            alias = loot_meta[name]["aliases"][0] if loot_meta[name]["aliases"] else loot_meta[name]["source_code"]
            rem_text = f" (Rem: {remaining})" if remaining is not None else ""
            
            line = f"{emoji} `{alias}` **{name}** | {cost}pts | {rule} | Stock: {stock if stock < 999 else '∞'}{rem_text}"
            
            if is_bidding:
                bid_lines.append(line)
            else:
                claim_lines.append(line)

        # Claim table - dynamically truncate to fit Discord limit
        claim_table = truncate_table(claim_lines, "CLAIM ITEMS")
        if claim_table.strip():
            embed.add_field(name="✅ Claim", value=claim_table, inline=False)

        # Bid table - dynamically truncate to fit Discord limit  
        bid_table = truncate_table(bid_lines, "BID ITEMS ( /bid [alias] [pts] )")
        if bid_table.strip():
            embed.add_field(name="⚔️ Bid", value=bid_table, inline=False)

        embed.description = f"💰 **Your Points: {user_pts}** | Filter: {filter}"
        embed.set_footer(text="`/itemlist` plain | `/points` | `/restock [item] [qty]` | `/impitems` upload more")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="itemlist", description="All loot items table (code/name/cost/rule/stock/rarity)")
    async def itemlist_cmd(interaction: discord.Interaction):
        embed = discord.Embed(title="📋 Loot Masterlist", color=discord.Color.blurple())
        
        claim_lines = []
        bid_lines = []

        for name in sorted(loot_meta):
            code = loot_meta[name]["source_code"]
            cost = loot_costs[name]["cost"]
            rule = loot_costs[name].get("rule", "")[:5]
            stock = loot_meta[name]["stock"]
            rarity = loot_meta[name]["rarity"][:6]
            
            line = f"`{code}` | {name[:20]} | {cost} | {rule} | {stock} | {rarity}"
            
            if loot_meta[name]["is_bidding"]:
                bid_lines.append(line)
            else:
                claim_lines.append(line)


        claim_table = "```\nCLAIM | CODE | NAME | COST | RULE | STOCK | RARITY\n" + "\n".join(claim_lines[:25]) + ( "\n... " + str(len(claim_lines)-25) + " more" if len(claim_lines) > 25 else "") + "\n```"
        bid_table = "```\nBID | CODE | NAME | COST | RULE | STOCK | RARITY\n" + "\n".join(bid_lines[:25]) + ( "\n... " + str(len(bid_lines)-25) + " more" if len(bid_lines) > 25 else "") + "\n```"

        embed.add_field(name=f"✅ Claim ({len(claim_lines)})", value=claim_table, inline=False)
        if bid_lines:
            embed.add_field(name=f"⚔️ Bid ({len(bid_lines)})", value=bid_table, inline=False)
        
        embed.set_footer(text="`/items` fancy | `/impitems` CSV upload | `/expitems` export")
        await interaction.response.send_message(embed=embed, ephemeral=True)

def get_emoji(name: str, rarity: str) -> str:
    emojis = {
        "common": "⚪",
        "uncommon": "🟢", 
        "rare": "🔵",
        "legendary": "🟣"
    }
    return emojis.get(rarity, "❓")

