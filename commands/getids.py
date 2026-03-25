import discord
import csv
import io

def setup(bot):
    @bot.tree.command(name="exportids", description="Moderator-only: Export all Discord IDs to CSV")
    async def export_ids_cmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message("❌ Only Moderators and Elders can use this command.", ephemeral=True)
            return

        # Build CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["member_id", "points"])  # header
        for member in interaction.guild.members:
            writer.writerow([member.id, 0])  # default points = 0

        # Send as file
        csv_file = discord.File(io.BytesIO(output.getvalue().encode()), filename="discord_ids.csv")
        await interaction.response.send_message("✅ Exported IDs to CSV:", file=csv_file, ephemeral=True)

    @bot.tree.command(name="getids", description="Moderator-only: Export attendance CSV template with all member IDs")
    async def get_ids_cmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message("❌ Only Moderators and Elders can use this command.", ephemeral=True)
            return

        # Build CSV template for attendance
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["member_id", "event", "outcome"])  # header
        for member in interaction.guild.members:
            writer.writerow([member.id, "", ""])  # empty event and outcome for manual filling

        # Send as file
        csv_file = discord.File(io.BytesIO(output.getvalue().encode()), filename="attendance_template.csv")
        await interaction.response.send_message(
            "✅ Exported attendance CSV template. Fill in 'event' and 'outcome' columns, then use /importattendance to upload.",
            file=csv_file,
            ephemeral=True
        )
