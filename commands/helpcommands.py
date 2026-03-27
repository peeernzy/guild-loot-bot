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
        
        # User Commands
        embed.add_field(
            name="🎮 User Commands",
            value="• `/points` - Check your points balance\n• `/leaderboard` - See top players by points\n• `/items` - Browse loot shop & codes\n• `/claim [code]` - Claim item (e.g. `/claim A1`)\n• `/bid [code] [pts]` - Bid points (e.g. `/bid A1 50`)\n• `/history` - Recent winners list\n• `/claimsleaderboard` - Active claims\n• `/bidsleaderboard` - Current bids",
            inline=False
        )
        
        # Player Actions
        embed.add_field(
            name="👥 Player Actions",
            value="• `/transfer @player [pts]` - Send points (e.g. `/transfer @friend 10`)\n• `/claimwinner [item]` - Spin random winner (admin)",
            inline=False
        )
        
        # Admin Commands
        embed.add_field(
            name="⚙️ Admin Commands",
            value="• `/addpoints @player [pts]` - Add points (Mod/Elder)\n• `/refundpoints @player [pts]` - Deduct points\n• `/impitems [csv]` - Import items from CSV\n• `/expitems` - Export items to CSV",
            inline=False
        )
        
        # Management
        embed.add_field(
            name="🔧 Management",
            value="• `/endbid [code]` - Close bids & award\n• `/award @player [item]` - Manual award\n• `/clearclaims` - Remove expired claims\n• `/reset` - Reset all data (careful!)",
            inline=False
        )
        
        embed.set_footer(text="Quick: `/cmd` user | `/acmd` admin | `/setpointlimit` limit | `/cls` clear | `/getids` IDs")
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="cmd", description="Quick user commands help")
    async def cmd(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="🎮 User Commands", color=discord.Color.green())
        cmds = [
            "• `/points` - Check your points balance",
            "• `/leaderboard` - See top players by points",
            "• `/items` - Browse loot shop & codes",
            "• `/claim [code]` - Claim item (e.g. `/claim A1`)",
            "• `/bid [code] [pts]` - Bid points (e.g. `/bid A1 50`)",
            "• `/history` - Recent winners list",
            "• `/claimsleaderboard` - Active claims",
            "• `/bidsleaderboard` - Current bids"
        ]
        embed.description = "\\n".join(cmds)
        embed.set_footer(text="• `/transfer @player [pts]` - Send points")
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
        cmds = [
            "• `/addpoints @player [pts]` - Add points",
            "• `/refundpoints @player [pts]` - Deduct points",
            "• `/impitems [csv]` - Import from CSV",
            "• `/expitems` - Export to CSV",
            "• `/endbid [code]` - Close bids",
            "• `/award @player [item]` - Manual award",
            "• `/cls` - Clear channel",
            "• `/getids` - Export IDs",
            "• `/setpointlimit [pts]` - Weekly limit",
            "• `/clearclaims` - Clean claims",
            "• `/reset` - Reset data"
        ]
        embed.description = "\\n".join(cmds)
        embed.set_footer(text="Events: `/setevent` `/listevents` | Attendance: `/importattendance`")
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="xid", description="View Discord ID")
    async def xid(interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer(ephemeral=True)
        member = member or interaction.user
        await interaction.followup.send(f"🆔 **{member.display_name}** ID: `{member.id}`")

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
