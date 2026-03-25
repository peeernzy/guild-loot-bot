import discord

def setup(bot):

    # Normal user commands (dynamic + categories)
    @bot.tree.command(name="ncmd", description="Show all commands available for normal users")
    async def normal_cmds(interaction: discord.Interaction):
        # Get all registered commands
        all_cmds = [cmd.name for cmd in bot.tree.get_commands()]

        # Define admin-only commands to exclude
        admin_cmds = {
            "getids", "exportids", "importcsv", "importattendance",
            "listevents", "setevent", "reset", "acmd"
        }

        # Filter out admin commands
        user_cmds = [c for c in all_cmds if c not in admin_cmds]

        # Group into categories
        gameplay = [f"/{c}" for c in user_cmds if c in {"points", "leaderboard", "items"}]
        info = [f"/{c}" for c in user_cmds if c in {"summary", "xid", "whois"}]

        lines = []
        if gameplay:
            lines.append("🎮 **Gameplay Commands**")
            lines.extend(gameplay)
        if info:
            lines.append("\n📊 **Information Commands**")
            lines.extend(info)

        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    # Admin commands (Moderator/Elder only, dynamic + categories)
    @bot.tree.command(name="acmd", description="Show all commands available for Moderators/Elders")
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
            "getids", "exportids", "importcsv", "importattendance",
            "listevents", "setevent", "reset"
        }

        cmds = [c for c in all_cmds if c in admin_cmds]

        # Group into categories
        attendance = [f"/{c}" for c in cmds if c in {"getids", "exportids", "importcsv", "importattendance"}]
        events = [f"/{c}" for c in cmds if c in {"listevents", "setevent"}]
        system = [f"/{c}" for c in cmds if c in {"reset"}]

        lines = []
        if attendance:
            lines.append("📝 **Attendance Tools**")
            lines.extend(attendance)
        if events:
            lines.append("\n📌 **Event Management**")
            lines.extend(events)
        if system:
            lines.append("\n⚙️ **System Tools**")
            lines.extend(system)

        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    # Extract ID command
    @bot.tree.command(name="xid", description="Extract and display a user's Discord ID")
    async def extract_id(interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(
            f"🆔 {member.display_name}'s Discord ID: `{member.id}`",
            ephemeral=True
        )

    # WhoIs command - identify user by ID
    @bot.tree.command(name="whois", description="Identify a user by their Discord ID")
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
