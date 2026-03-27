import discord
import csv
import io

def setup(bot):
    @bot.tree.command(name="getids", description="Moderator-only: Export attendance CSV template for Farmers only")
    async def get_ids_cmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message("❌ Only Moderators and Elders can use this command.", ephemeral=True)
            return

        # Build CSV template for attendance (Farmers only)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["display_name", "username", "member_id", "event", "outcome"])  # header
        
        farmers_count = 0
        for member in interaction.guild.members:
            # Check if member has "Farmers" or "farmers" role (case insensitive)
            member_roles = [role.name.lower() for role in member.roles]
            if "farmers" in member_roles:
                writer.writerow([member.display_name, member.name, member.id, "", ""])  # empty event and outcome for manual filling
                farmers_count += 1

        # Send as file
        csv_file = discord.File(io.BytesIO(output.getvalue().encode()), filename="farmers_attendance_template.csv")
        await interaction.response.send_message(
            f"✅ Exported attendance CSV template for **{farmers_count} Farmers**. Fill in 'event' and 'outcome' columns, then use /importattendance to upload.",
            file=csv_file,
            ephemeral=True
        )

