import discord

COMMAND_DETAILS = {
    "points": "View your current loot points balance.",
    "addpoints": "Add points to a member account (admin).",
    "refundpoints": "Deduct points from a member (admin).",
    "leaderboard": "See the current guild rankings by points.",
    "inventory": "Browse the available loot items and rewards.",
    "inventory_list": "Simple table of all loot items (code/name/cost/rule/stock/rarity).",
    "stock": "Check single item stock.",
    "restock": "Restock item stock (Mod/Elder).",
    "claim": "Claim an available loot item using its code.",
    "claimcancel": "Cancel your claim (refund points).",
    "bid": "Place a bid on a loot item.",
    "bidcancel": "Cancel your bid (refund points).",
    "claimsleaderboard": "View the current list of active loot claims.",
    "bidsleaderboard": "View the current bidding standings.",
    "history": "View recent winners history.",
    "transfer": "Transfer your points to another player.",
    "claimwinner": "Roll 1-100 spin to pick claim winner with ranking.",
    "allclanpoints": "Show all clan member points balances.",
    "setpointlimit": "Set weekly point spending limit.",
    "price": "Check item prices.",
    "xid": "Display your Discord ID or another member's ID.",
    "whois": "Look up a member using their Discord ID.",
    "getids": "Generate the member ID list for attendance tracking.",
    "expitems": "Export loot items to CSV.",
    "impitems": "Import loot items from CSV with backup.",
    "item_export": "Alias for /expitems.",
    "item_import": "Alias for /impitems.",
    "importattendance": "Upload and process attendance records.",
    "listevents": "View the list of configured guild events.",
    "setevent": "Create or update the active event setup.",
    "endbid": "Close bidding and award the highest bidder.",
    "award": "Manually award an item to a selected member.",
    "clearclaims": "Remove expired loot claims.",
    "cls": "Clear all messages in current channel.",
    "grant": "Grant a loot item directly (admin).",
    "reset": "Reset bot tracking data when needed.",
    "summary": "Guild event summary.",
}

USER_CMDS = {
    "points": COMMAND_DETAILS["points"],
    "inventory": COMMAND_DETAILS["inventory"],
    "inventory_list": COMMAND_DETAILS["inventory_list"],
    "stock": COMMAND_DETAILS["stock"],
    "claim": COMMAND_DETAILS["claim"],
    "claimcancel": COMMAND_DETAILS["claimcancel"],
    "bid": COMMAND_DETAILS["bid"],
    "bidcancel": COMMAND_DETAILS["bidcancel"],
    "claimsleaderboard": COMMAND_DETAILS["claimsleaderboard"],
    "bidsleaderboard": COMMAND_DETAILS["bidsleaderboard"],
    "history": COMMAND_DETAILS["history"],
    "transfer": COMMAND_DETAILS["transfer"],
    "leaderboard": COMMAND_DETAILS["leaderboard"]
}

ADMIN_CMDS = {
    "addpoints": COMMAND_DETAILS["addpoints"],
    "refundpoints": COMMAND_DETAILS["refundpoints"],
    "expitems": COMMAND_DETAILS["expitems"],
    "impitems": COMMAND_DETAILS["impitems"],
    "restock": COMMAND_DETAILS["restock"],
    "reloaditems": "Reload loot items from DB (sync command).",
    "endbid": COMMAND_DETAILS["endbid"],
    "award": COMMAND_DETAILS["award"],
    "clearclaims": COMMAND_DETAILS["clearclaims"],
    "cls": COMMAND_DETAILS["cls"],
    "reset": COMMAND_DETAILS["reset"],
    "getids": COMMAND_DETAILS["getids"]
}

EVENT_CMDS = {
    "summary": COMMAND_DETAILS["summary"],
    "setpointlimit": COMMAND_DETAILS["setpointlimit"],
    "price": COMMAND_DETAILS["price"],
    "importattendance": COMMAND_DETAILS["importattendance"],
    "listevents": COMMAND_DETAILS["listevents"],
    "setevent": COMMAND_DETAILS["setevent"]
}

def setup(bot):

    @bot.tree.command(name="masterlist", description="Full list of all slash commands")
    async def masterlist_cmd(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="📋 All Slash Commands", color=discord.Color.blue())
        
        embed.add_field(
            name="🎮 User Commands",
            value="`/inventory` - Browse loot shop\n`/inventory_list` - Full table\n`/stock [code]` - Item stock\n`/claim [code]` - Claim\n`/bid [code] [pts]` - Bid\n`/claimcancel [code]` - Cancel claim\n`/bidcancel [code]` - Cancel bid\n`/points` - Balance\n`/leaderboard` - Top players\n`/history` - Winners\n`/transfer @player [pts]` - Send points\n`/claimsleaderboard` - Claims list\n`/bidsleaderboard` - Bids list",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Admin (Mod/Elder)",
            value="`/addpoints @player [pts]` - Add points\n`/refundpoints @player [pts]` - Deduct\n`/impitems [csv] force:true` - CSV import\n`/expitems` - Export CSV\n`/restock [code] [stock]` - Restock\n`/reloaditems` - Reload DB\n`/endbid [item]` - Close bid\n`/award [item] @player` - Award\n`/clearclaims` - Clear expired\n`/reset` - Reset data\n`/cls` - Clear chat\n`/getids` - ID list",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Events",
            value="`/summary` - Event stats\n`/setevent` - Setup event\n`/listevents` - List events\n`/attendance` - Track attendance",
            inline=False
        )
        
        embed.set_footer(text="Quick: `/cmd` user | `/acmd` admin | Full: `/masterlist`")
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="cmd", description="User commands help")
    async def cmd(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="🎮 User Commands", color=discord.Color.green())
        embed.add_field(
            name="Loot Actions",
            value="`/inventory` - Shop\n`/claim [code]` - Claim\n`/bid [code] [pts]` - Bid\n`/claimcancel [code]` - Cancel claim\n`/bidcancel [code]` - Cancel bid",
            inline=False
        )
        embed.add_field(
            name="Info",
            value="`/points` - Balance\n`/stock [code]` - Stock\n`/leaderboard` - Top\n`/history` - Winners\n`/claimsleaderboard` - Claims\n`/bidsleaderboard` - Bids",
            inline=False
        )
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="acmd", description="Admin commands help")
    async def acmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ Mod/Elder only", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="⚙️ Admin Commands", color=discord.Color.orange())
        embed.add_field(
            name="Items",
            value="`/impitems [csv] force:true` - Import\n`/expitems` - Export\n`/restock [code] [stock]` - Restock\n`/reloaditems` - Reload",
            inline=False
        )
        embed.add_field(
            name="Management",
            value="`/addpoints/refundpoints` - Points\n`/endbid [item]` - Close bid\n`/award [item] @player` - Award\n`/clearclaims` - Clear expired\n`/reset` - Reset\n`/cls` - Clear chat",
            inline=False
        )
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="xid", description="View Discord ID")
    async def xid(interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer(ephemeral=True)
        member = member or interaction.user
        await interaction.followup.send(f"🆔 **{member.display_name}**\\nID: `{member.id}`")

    @bot.tree.command(name="whois", description="Look up user by ID")
    async def whois(interaction: discord.Interaction, user_id: str):
        await interaction.response.defer(ephemeral=True)
        try:
            uid = int(user_id.strip())
            member = interaction.guild.get_member(uid)
            if member:
                await interaction.followup.send(f"👤 **{member.display_name}**\\nID: `{uid}`\\nJoined: {member.joined_at}")
            else:
                await interaction.followup.send(f"❌ User {uid} not in server")
        except ValueError:
            await interaction.followup.send("❌ Invalid ID")

