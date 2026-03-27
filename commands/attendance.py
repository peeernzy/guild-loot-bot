import discord
import csv
import io
import json
from .points import add_points

EVENTS_FILE = "events.json"

# Load event rules into memory
def load_event_rules():
    try:
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

EVENT_RULES = load_event_rules()

def setup(bot):

    @bot.tree.command(name="importattendance", description="Moderator-only: Import attendance with events/outcomes")
    async def import_attendance_cmd(interaction: discord.Interaction, file: discord.Attachment):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ Only Moderators and Elders can import attendance.", ephemeral=True)
            return

        data = await file.read()
        text = data.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))

        updates = []
        for row in reader:
            member_id = int(row["member_id"])
            raw_event = row["event"].strip().lower()
            raw_outcome = row["outcome"].strip().lower()

            # Event aliases
            event_alias = {
                "1": "clansanctuary",
                "2": "sindrisisland",
                "clansanctuary": "clansanctuary",
                "sindrisisland": "sindris island"
            }

            # Outcome aliases (new codes + old)
            outcome_alias = {
                "1": "win",
                "0": "lose",
                "10": "participated",
                "11": "absent",
                "20": "participated",
                "21": "lose",
                "22": "absent",
                "win": "win",
                "lose": "lose",
                "participated": "participated",
                "absent": "absent"
            }

            event = event_alias.get(raw_event, raw_event)
            outcome = outcome_alias.get(raw_outcome, raw_outcome)

            # Lookup points from config
            points = EVENT_RULES.get(event, {}).get(outcome, 0)

            member = interaction.guild.get_member(member_id)
            if member and points > 0:
                new_balance = add_points(member.id, points)
                updates.append(f"{member.display_name}: {new_balance} (+{points})")

        if updates:
            await interaction.response.send_message("✅ Attendance imported:\n" + "\n".join(updates))
        else:
            await interaction.response.send_message("❌ No valid members found in CSV.")

    @bot.tree.command(name="listevents", description="Moderator-only: Show all event point rules")
    async def list_events_cmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ Only Moderators and Elders can view event rules.", ephemeral=True)
            return

        lines = []
        for event, outcomes in EVENT_RULES.items():
            lines.append(f"📌 **{event.capitalize()}**")
            for outcome, points in outcomes.items():
                lines.append(f"  ipel - {outcome}: {points} points")

        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @bot.tree.command(name="setevent", description="Moderator-only: Update event point rules")
    async def set_event_cmd(interaction: discord.Interaction, event: str, outcome: str, points: int):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)
        if not has_permission:
            await interaction.response.send_message("❌ Only Moderators and Elders can update event rules.", ephemeral=True)
            return

        # Normalize keys
        event = event.strip().lower()
        outcome = outcome.strip().lower()

        # Update in memory
        if event not in EVENT_RULES:
            EVENT_RULES[event] = {}
        EVENT_RULES[event][outcome] = points

        # Save back to JSON
        with open(EVENTS_FILE, "w") as f:
            json.dump(EVENT_RULES, f, indent=4)

        await interaction.response.send_message(
            f"✅ Updated rule: **{event} → {outcome} = {points} points** (active immediately)",
            ephemeral=True
        )

