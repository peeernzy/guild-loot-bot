import discord

COMMAND_DETAILS = {
    "points": "View your current loot points balance.",
    "leaderboard": "See the current guild rankings by points.",
    "items": "Browse the available loot items and rewards.",
    "claim": "Claim an available loot item using its code.",
    "bid": "Place a bid on a loot item.",
    "claimsleaderboard": "View the current list of active loot claims.",
    "bidsleaderboard": "View the current bidding standings.",
    "summary": "Check the latest event and loot summary.",
    "xid": "Display your Discord ID or another member's ID.",
    "whois": "Look up a member using their Discord ID.",
    "add": "Add points to a member account.",
    "refund": "Deduct points from a member.",
    "grant": "Award a loot item directly to a member.",
    "getids": "Generate the member ID list for attendance tracking.",
    "exportids": "Export saved member IDs for record keeping.",
    "importcsv": "Import attendance data from a CSV file.",
    "importattendance": "Upload and process attendance records.",
    "listevents": "View the list of configured guild events.",
    "setevent": "Create or update the active event setup.",
    "endbid": "Close bidding and award the highest bidder.",
    "award": "Manually award an item to a selected member.",
    "clearclaims": "Remove expired loot claims.",
    "reset": "Reset bot tracking data when needed.",
}

def setup(bot):

    # Normal user commands (dynamic + categories)
    @bot.tree.command(name="ncmd", description="View user commands")
    async def normal_cmds(interaction: discord.Interaction):
        # Get all registered commands
        all_cmds = [cmd.name for cmd in bot.tree.get_commands()]

        # Define admin-only commands to exclude
        admin_cmds = {
            "add", "refund", "grant", "getids", "exportids", "importcsv", "importattendance",
            "listevents", "setevent", "endbid", "award", "clearclaims",
            "reset", "xid", "whois", "acmd"
        }

        # Filter out admin commands
        user_cmds = [c for c in all_cmds if c not in admin_cmds]

        # Group into categories
        gameplay = [f"/{c}" for c in user_cmds if c in {"points", "leaderboard", "items", "claim", "bid", "claimsleaderboard", "bidsleaderboard"}]
        info = [f"/{c}" for c in user_cmds if c in {"summary"}]

        lines = ["## Normal User Commands", "Clean access to your everyday guild tools.\n"]

        if gameplay:
            lines.append("🎮 **Gameplay Commands**")
            lines.extend(f"• {cmd} — {COMMAND_DETAILS.get(cmd[1:], 'No description available.')}" for cmd in gameplay)

        if info:
            lines.append("")
            lines.append("📊 **Information Commands**")
            lines.extend(f"• {cmd} — {COMMAND_DETAILS.get(cmd[1:], 'No description available.')}" for cmd in info)

        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    # Admin commands (Moderator/Elder only, dynamic + categories)
    @bot.tree.command(name="acmd", description="View admin commands")
    async def admin_cmds(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ Only Moderators and Elders can view admin commands.", ephemeral=True)
            return

        # Get all registered commands
        all_cmds = [cmd.name for cmd in bot.tree.get_commands()]

        # Define admin-only commands
        admin_cmds = {
            "add", "refund", "grant", "getids", "exportids", "importcsv", "importattendance",
            "listevents", "setevent", "endbid", "award", "clearclaims",
            "reset", "xid", "whois"
        }

        cmds = [c for c in all_cmds if c in admin_cmds]

        # Group into categories
        points_tools = [f"/{c}" for c in cmds if c in {"add", "refund"}]
        loot_tools = [f"/{c}" for c in cmds if c in {"grant", "endbid", "award", "clearclaims"}]
        attendance = [f"/{c}" for c in cmds if c in {"getids", "exportids", "importcsv", "importattendance"}]
        events = [f"/{c}" for c in cmds if c in {"listevents", "setevent"}]
        system = [f"/{c}" for c in cmds if c in {"reset"}]
        member_tools = [f"/{c}" for c in cmds if c in {"xid", "whois"}]

        lines = ["## Admin Commands", "Administrative tools for Moderators and Elders.\n"]

        if points_tools:
            lines.append("💰 **Points Management**")
            lines.extend(f"• {cmd} — {COMMAND_DETAILS.get(cmd[1:], 'No description available.')}" for cmd in points_tools)

        if loot_tools:
            lines.append("")
            lines.append("🎁 **Loot Management**")
            lines.extend(f"• {cmd} — {COMMAND_DETAILS.get(cmd[1:], 'No description available.')}" for cmd in loot_tools)

        if attendance:
            lines.append("")
            lines.append("📝 **Attendance Tools**")
            lines.extend(f"• {cmd} — {COMMAND_DETAILS.get(cmd[1:], 'No description available.')}" for cmd in attendance)

        if events:
            lines.append("")
            lines.append("📌 **Event Management**")
            lines.extend(f"• {cmd} — {COMMAND_DETAILS.get(cmd[1:], 'No description available.')}" for cmd in events)

        if member_tools:
            lines.append("")
            lines.append("👤 **Member Tools**")
            lines.extend(f"• {cmd} — {COMMAND_DETAILS.get(cmd[1:], 'No description available.')}" for cmd in member_tools)

        if system:
            lines.append("")
            lines.append("⚙️ **System Tools**")
            lines.extend(f"• {cmd} — {COMMAND_DETAILS.get(cmd[1:], 'No description available.')}" for cmd in system)

        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    # Extract ID command
    @bot.tree.command(name="xid", description="View a Discord ID")
    async def extract_id(interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(
            f"🆔 {member.display_name}'s Discord ID: `{member.id}`",
            ephemeral=True
        )

    # WhoIs command - identify user by ID
    @bot.tree.command(name="whois", description="Look up a user by ID")
    async def whois(interaction: discord.Interaction, user_id: str):
        try:
            # Convert string to int
            uid = int(user_id.strip())

            # Try to get member from guild
            member = interaction.guild.get_member(uid)

            if member:
                # Member is in the server
                response = f"👤 **User Information:**\n"
                response += f"**Display Name:** {member.display_name}\n"
                response += f"**Username:** {member.name}\n"
                response += f"**User ID:** `{member.id}`\n"
                response += f"**Joined Server:** {member.joined_at.strftime('%Y-%m-%d %H:%M UTC') if member.joined_at else 'Unknown'}\n"
                response += f"**Account Created:** {member.created_at.strftime('%Y-%m-%d %H:%M UTC') if member.created_at else 'Unknown'}\n"
                response += f"**Roles:** {', '.join([role.name for role in member.roles[1:]]) if len(member.roles) > 1 else 'None'}"
            else:
                # Member not in server, but we can still show basic info if bot has access
                user = bot.get_user(uid)
                if user:
                    response = f"👤 **User Information (Not in Server):**\n"
                    response += f"**Username:** {user.name}\n"
                    response += f"**User ID:** `{user.id}`\n"
                    response += f"**Account Created:** {user.created_at.strftime('%Y-%m-%d %H:%M UTC') if user.created_at else 'Unknown'}\n"
                    response += f"**Bot:** {'Yes' if user.bot else 'No'}"
                else:
                    response = f"❌ **User not found:** `{user_id}`\n\nUnable to find a user with this ID. They may not be in any servers the bot can access."

        except ValueError:
            response = f"❌ **Invalid ID format:** `{user_id}`\n\nPlease provide a valid Discord user ID (numbers only)."

        await interaction.response.send_message(response, ephemeral=True)
