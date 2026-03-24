import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

points = {}
claims = {}
bids = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)

# -----------------------------
# POINTS COMMANDS
# -----------------------------
@bot.tree.command(name="points", description="Check a member's points")
async def points_cmd(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    balance = points.get(member.id, 0)
    await interaction.response.send_message(f"{member.display_name} has {balance} points.")

@bot.tree.command(name="add", description="Add points to a member")
async def add_cmd(interaction: discord.Interaction, member: discord.Member, amount: int):
    # Restrict to Moderator or Elder roles
    allowed_roles = ["Moderator", "Elder"]
    has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

    if not has_permission:
        await interaction.response.send_message(
            "❌ Only Moderators and Elders can add points.",
            ephemeral=True
        )
        print(f"[SECURITY] {interaction.user} tried to use /add without permission.")
        return

    points[member.id] = points.get(member.id, 0) + amount
    await interaction.response.send_message(f"✅ Added {amount} points to {member.display_name}.")
    print(f"[LOG] {interaction.user} added {amount} points to {member.display_name}.")

# -----------------------------
# TEST COMMAND (Moderator Only)
# -----------------------------
@bot.tree.command(name="testpoints", description="Test adding or subtracting points (Moderator only)")
async def testpoints_cmd(interaction: discord.Interaction, member: discord.Member, amount: int):
    # Restrict to Moderator role only
    has_permission = any(role.name == "Moderator" for role in interaction.user.roles)

    if not has_permission:
        await interaction.response.send_message(
            "❌ Only Moderators can run testpoints.",
            ephemeral=True
        )
        print(f"[SECURITY] {interaction.user} tried to use /testpoints without permission.")
        return

    points[member.id] = points.get(member.id, 0) + amount
    await interaction.response.send_message(
        f"🧪 Test: {amount:+} points applied to {member.display_name}."
    )
    print(f"[TEST LOG] {interaction.user} applied {amount:+} test points to {member.display_name}.")

# -----------------------------
# LOOT COMMANDS
# -----------------------------
@bot.tree.command(name="claim", description="Claim loot items")
async def claim_cmd(interaction: discord.Interaction, item: str):
    user_id = interaction.user.id
    claims[user_id] = claims.get(user_id, [])
    claims[user_id].append(item)
    await interaction.response.send_message(f"{interaction.user.display_name} claimed {item}!")

@bot.tree.command(name="spin", description="Spin for rare equipment")
async def spin_cmd(interaction: discord.Interaction):
    if not claims:
        await interaction.response.send_message("No one joined the spin yet!")
        return
    winner_id = random.choice(list(claims.keys()))
    winner = await interaction.guild.fetch_member(winner_id)
    await interaction.response.send_message(f"🎉 {winner.display_name} won the spin!")

# -----------------------------
# SUMMARY COMMAND
# -----------------------------
@bot.tree.command(name="summary", description="Show all balances")
async def summary_cmd(interaction: discord.Interaction):
    if not points:
        await interaction.response.send_message("No points recorded yet.")
        return
    summary = "\n".join([
        f"{interaction.guild.get_member(uid).display_name}: {pts}"
        for uid, pts in points.items()
        if interaction.guild.get_member(uid) is not None
    ])
    await interaction.response.send_message(f"📊 Points Summary:\n{summary}")

bot.run(os.getenv("BOT_TOKEN"))
