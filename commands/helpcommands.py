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
        info = [f"/{c}" for c in user_cmds if c in {"summary", "xid"}]

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
