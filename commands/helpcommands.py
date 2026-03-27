import discord

COMMAND_DETAILS = {
    "points": "View your current loot points balance.",
    "addpoints": "Add points to a member account (admin).",
    "refundpoints": "Deduct points from a member (admin).",
    "leaderboard": "See the current guild rankings by points.",
    "items": "Browse the available loot items and rewards.",
    "itemlist": "Simple table of all loot items (code/name/cost/rule/stock/rarity).",
    "stock": "Check single item stock.",
    "restock": "Restock item stock (Mod/Elder).",
    "claim": "Claim an available loot item using its code.",
    "bid": "Place a bid on a loot item.",
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

def setup(bot):
    @bot.tree.command(name="masterlist", description="Full list of all slash commands")
    async def masterlist_cmd(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="📋 All Slash Commands", color=discord.Color.blue())
        
        embed.add_field(
            name="🎮 User Commands",
            value="• `/points` - Points balance\n• `/leaderboard` - Top players\n• `/items` - Fancy loot shop\n• `/itemlist` - Items table\n• `/stock [code]` - Item stock\n• `/claim [code]` - Claim\n• `/bid [code] [pts]` - Bid\n• `/history` - Winners\n• `/claimsleaderboard` - Claims\n• `/bidsleaderboard` - Bids",
            inline=False
        )
        
        embed.add_field(
            name="👥 Player Actions",
            value="• `/transfer @player [pts]` - Send points",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Admin Commands (Mod/Elder)",
            value="• `/addpoints/@refundpoints [pts]` - Points mgmt\n• `/restock [item] [qty]` - Restock\n• `/impitems/expitems [CSV]` - Import/Export\n• `/cls` - Clear channel\n• `/getids` - IDs list\n• `/setpointlimit` - Weekly limit",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Management",
            value="• `/endbid/award/clearclaims/reset` - Event mgmt\n• `/summary/attendance/setevent/listevents` - Events",
            inline=False
        )
        
        embed.set_footer(text="`/cmd` user | `/acmd` admin | `/xid/@whois` utils | Full: `/helpcommands`")
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="cmd", description="Quick user commands")
    async def cmd(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="🎮 User Commands", color=discord.Color.green())
        embed.add_field(
            name="Loot & Points",
            value="• `/points` • `/leaderboard` • `/items` • `/itemlist`\n• `/stock [code]` • `/claim [code]` • `/bid`\n• `/history` • `/transfer` • claims/bids leaderboards",
            inline=False
        )
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="acmd", description="Quick admin commands (Mod/Elder)")
    async def acmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ Mod/Elder only", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="⚙️ Admin Commands", color=discord.Color.orange())
        embed.add_field(
            name="Points & Items",
            value="• `/addpoints/refundpoints`\n• `/restock [item] [qty]`\n• `/impitems/expitems [CSV]`",
            inline=False
        )
        embed.add_field(
            name="Management",
            value="• `/cls` • `/getids` • `/setpointlimit`\n• `/endbid/award/clearclaims/reset`\n• Events: `/summary/setevent/listevents`",
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

