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
        desc = "**🏆 Guild Loot Bot - Full Slash Commands**\n\n"
        desc += "**🎮 User Commands:**\n"
        user_cmds = [
            "points - Check balance",
            "leaderboard - Top players",
            "items - Loot shop",
            "claim [code] - Claim item",
            "bid [code] [amount] - Bid points",
            "history [limit] - Recent winners",
            "claimsleaderboard - Active claims",
            "bidsleaderboard - Bid standings",
            "transfer [@player pts] - Send points",
            "claimwinner [item] - Spin winner"
        ]
        desc += " • " + "\n • ".join(user_cmds) + "\n\n"
        
        desc += "**⚙️ Admin Commands (Mod/Elder):**\n"
        admin_cmds = [
            "addpoints/refundpoints - Manage points",
            "impitems [csv] - Import items",
            "expitems - Export items",
            "endbid/award/clearclaims - Loot management",
            "reset - Reset data",
            "setpointlimit - Set spend limit",
            "cls - Clear channel",
            "getids/xid/whois - ID tools",
            "acmd - Admin help"
        ]
        desc += " • " + "\n • ".join(admin_cmds) + "\n\n"
        
        desc += "**Use `/cmd` for user help, `/acmd` for admin details.**"
        
        embed = discord.Embed(title="📋 Master Command List", description=desc, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="cmd", description="View user commands")
    async def cmd(interaction: discord.Interaction):
        lines = ["**User Commands:**"]
        lines.append("• `/points` - Balance")
        lines.append("• `/leaderboard` - Top players")
        lines.append("• `/items` - Loot shop")
        lines.append("• `/claim [code]` - Claim item")
        lines.append("• `/bid [code] [pts]` - Bid")
        lines.append("• `/history` - Winners")
        lines.append("• `/claimsleaderboard` - Claims")
        lines.append("• `/bidsleaderboard` - Bids")
        lines.append("• `/transfer @player pts` - Send pts")
        lines.append("• `/claimwinner [item]` - Spin winner")
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @bot.tree.command(name="acmd", description="View admin commands")
    async def acmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ Admin only.", ephemeral=True)
            return
        lines = ["**Admin Commands:**"]
        lines.append("• `/addpoints`/`refundpoints` - Points mgmt")
        lines.append("• `/impitems`/`expitems` - Item lists")
        lines.append("• `/endbid`/`award`/`clearclaims` - Loot")
        lines.append("• `/reset`/`setpointlimit` - Settings")
        lines.append("• `/cls` - Clear channel")
        lines.append("• `/getids`/`listevents`/`setevent` - Events")
        lines.append("• `/importattendance` - CSV")
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @bot.tree.command(name="xid", description="View Discord ID")
    async def xid(interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(f"🆔 {member.display_name}: `{member.id}`", ephemeral=True)

    @bot.tree.command(name="whois", description="Look up user by ID")
    async def whois(interaction: discord.Interaction, user_id: str):
        try:
            uid = int(user_id.strip())
            member = interaction.guild.get_member(uid)
            if member:
                await interaction.response.send_message(f"👤 {member.display_name} (ID: {uid})\nJoined: {member.joined_at}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ User {uid} not in server.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid ID", ephemeral=True)

