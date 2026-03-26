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
"allclanpoints": "Show all clan member points balances.",
    "setpointlimit": "Set weekly point spending limit.",
    "price": "Check item prices.",
    "xid": "Display your Discord ID or another member's ID.",
    "whois": "Look up a member using their Discord ID.",
    "getids": "Generate the member ID list for attendance tracking.",
    "exportids": "Export saved member IDs for record keeping.",
    "importattendance": "Upload and process attendance records.",
    "listevents": "View the list of configured guild events.",
    "setevent": "Create or update the active event setup.",
    "endbid": "Close bidding and award the highest bidder.",
    "award": "Manually award an item to a selected member.",
    "clearclaims": "Remove expired loot claims.",
    "cls": "Clear all messages in current channel.",
    "impitems": "Import loot items from CSV with backup.",
    "expitems": "Export loot items to CSV.",
    "grant": "Grant a loot item directly (admin).",
    "reset": "Reset bot tracking data when needed.",
}

def setup(bot):
    @bot.tree.command(name="cmd", description="View user commands")
    async def cmd(interaction: discord.Interaction):
        all_cmds = [cmd.name for cmd in bot.tree.get_commands()]
        admin_cmds = {
            "addpoints", "refundpoints", "grant", "getids", "exportids", "importattendance",
            "listevents", "setevent", "endbid", "award", "clearclaims", "cls", "impitems", "expitems",
            "reset", "xid", "whois", "acmd"
        }
        user_cmds = [c for c in all_cmds if c not in admin_cmds]
        gameplay = [f"/{c}" for c in user_cmds if c in {"points", "leaderboard", "items", "claim", "bid", "claimsleaderboard", "bidsleaderboard", "history"}]
        info = [f"/{c}" for c in user_cmds if c in {"allclanpoints", "price"}]
        lines = ["## User Commands", ""]
        if gameplay:
            lines.append("🎮 Gameplay")
            lines.extend(f"• {cmd}: {COMMAND_DETAILS.get(cmd[1:], '?')}" for cmd in gameplay)
        if info:
            lines.append("📊 Info")
            lines.extend(f"• {cmd}: {COMMAND_DETAILS.get(cmd[1:], '?')}" for cmd in info)
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @bot.tree.command(name="acmd", description="View admin commands")
    async def acmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ Admin only.", ephemeral=True)
            return
        all_cmds = [cmd.name for cmd in bot.tree.get_commands()]
        admin_cmds = {
            "addpoints", "refundpoints", "grant", "getids", "exportids", "importattendance",
            "listevents", "setevent", "endbid", "award", "clearclaims", "cls", "impitems", "expitems",
            "reset", "xid", "whois"
        }
        cmds = [c for c in all_cmds if c in admin_cmds]
        points = [f"/{c}" for c in cmds if c in {"addpoints", "refundpoints"}]
        loot = [f"/{c}" for c in cmds if c in {"grant", "endbid", "award", "clearclaims"}]
        system = [f"/{c}" for c in cmds if c in {"cls", "reset", "impitems"}]
        lines = ["## Admin Commands", ""]
        if points:
            lines.append("💰 Points")
            lines.extend(f"• {cmd}: {COMMAND_DETAILS.get(cmd[1:], '?')}" for cmd in points)
        if loot:
            lines.append("🎁 Loot")
            lines.extend(f"• {cmd}: {COMMAND_DETAILS.get(cmd[1:], '?')}" for cmd in loot)
        if system:
            lines.append("⚙️ System")
            lines.extend(f"• {cmd}: {COMMAND_DETAILS.get(cmd[1:], '?')}" for cmd in system)
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

