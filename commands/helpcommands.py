import discord

COMMAND_DETAILS = {
    "points": "View your current loot points balance.",
    "addpoints": "Add points to a member account (admin).",
    "refundpoints": "Deduct points from a member (admin).",
    "leaderboard": "See the current guild rankings by points.",
    "items": "Browse the available loot items and rewards.",
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
    "importattendance": "Upload and process attendance records.",
    "listevents": "View the list of configured guild events.",
    "setevent": "Create or update the active event setup.",
    "endbid": "Close bidding and award the highest bidder.",
    "award": "Manually award an item to a selected member.",
    "clearclaims": "Remove expired loot claims.",
    "cls": "Clear all messages in current channel.",
    "impitems": "Import loot items from CSV with backup.",
    "grant": "Grant a loot item directly (admin).",
    "reset": "Reset bot tracking data when needed.",
    "summary": "Guild event summary.",
}

def setup(bot):
    @bot.tree.command(name="masterlist", description="Full list of all slash commands")
    async def masterlist_cmd(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="📋 All Slash Commands", color=discord.Color.blue())
        
        # User commands
        user_cmds = [
            "• **`/points`** - Check your points balance",
            "• **`/leaderboard`** - See top players by points",
            "• **`/items`** - Browse loot shop & codes",
            "• **`/claim [code]`** - Claim item (e.g. `/claim A1`)",
            "• **`/bid [code] [pts]`** - Bid points (e.g. `/bid A1 50`)",
            "• **`/history`** - Recent winners list",
            "• **`/claimsleaderboard`** - Active claims",
            "• **`/bidsleaderboard`** - Current bids"
        ]
        embed.add_field(name="🎮 User Commands", value="\\n".join(user_cmds), inline=False)
        
        # Player actions
        player_cmds = [
            "• **`/transfer @player [pts]`** - Send points (e.g. `/transfer @friend 10`)",
            "• **`/claimwinner [item]`** - Spin random winner (admin)"
        ]
        embed.add_field(name="👥 Player Actions", value="\\n".join(player_cmds), inline=False)
        
        # Admin commands
        admin_cmds = [
            "• **`/addpoints @player [pts]`** - Add points (Mod/Elder)",
            "• **`/refundpoints @player [pts]`** - Deduct points",
            "• **`/impitems [csv]`** - Import items from CSV",
            "• **`/expitems`** - Export items to CSV"
        ]
        embed.add_field(name="⚙️ Admin Commands", value="\\n".join(admin_cmds), inline=False)
        
        # Management
        mgmt_cmds = [
            "• **`/endbid [code]`** - Close bids & award",
            "• **`/award @player [item]`** - Manual award",
            "• **`/clearclaims`** - Remove expired claims",
            "• **`/reset`** - Reset all data (careful!)"
        ]
        embed.add_field(name="🔧 Management", value="\\n".join(mgmt_cmds), inline=False)
        
        embed.set_footer(text="Use /cmd or /acmd for quick views • Mod/Elder = Moderator or Elder role")
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="cmd", description="Quick user commands help")
    async def cmd(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="🎮 User Commands", color=discord.Color.green())
        cmds = [
            "**`/points`** - Your balance",
            "**`/leaderboard`** - Top ranks",
            "**`/items`** - Shop & codes",
            "**`/claim [code]`** - Claim (e.g. A1)",
            "**`/bid [code] [pts]`** - Bid (e.g. A1 50)",
            "**`/history`** - Past winners",
            "**`/claimsleaderboard`** / **`/bidsleaderboard`** - Live status"
        ]
        embed.description = "\\n".join(cmds)
        embed.set_footer(text="`/transfer @player pts` - Send points")
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="acmd", description="Quick admin commands help (Mod/Elder)")
    async def acmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ Admin only.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="⚙️ Admin Commands", color=discord.Color.orange())
        cmds = [
            "**`/addpoints`/`refundpoints @player pts`** - Points management",
            "**`/impitems [csv]`** - Import items",
            "**`/expitems`** - Export items",
            "**`/endbid [code]`** - Close & award bids",
            "**`/award @player [item]`** - Manual give",
            "**`/cls`** - Clear channel messages",
            "**`/getids`** - Export member IDs",
            "**`/setpointlimit [pts]`** - Weekly limit"
        ]
        embed.description = "\\n".join(cmds)
        embed.set_footer(text="Events: `/setevent`, `/listevents` • Attendance: `/importattendance`")
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="xid", description="View Discord ID")
    async def xid(interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer(ephemeral=True)
        member = member or interaction.user
        await interaction.followup.send(f"🆔 **{member.display_name}**: `{member.id}`")

    @bot.tree.command(name="whois", description="Look up user by ID")
    async def whois(interaction: discord.Interaction, user_id: str):
        await interaction.response.defer(ephemeral=True)
        try:
            uid = int(user_id.strip())
            member = interaction.guild.get_member(uid)
            if member:
                await interaction.followup.send(f"👤 **{member.display_name}** (ID: `{uid}`)\\n📅 Joined: {member.joined_at}")
            else:
                await interaction.followup.send(f"❌ User {uid} not found in server.")
        except ValueError:
            await interaction.followup.send("❌ Invalid ID format. Use numbers only.")
