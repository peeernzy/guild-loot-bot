import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# BOT SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # needed for role checks and summaries
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# IMPORT COMMAND MODULES
# =========================
# Each module should only define its own commands
from commands import points, loot, leaderboard, items, summary, reset, attendance, getids, helpcommands

# Register commands from each module
points.setup(bot)
loot.setup(bot)
leaderboard.setup(bot)
items.setup(bot)
summary.setup(bot)
reset.setup(bot)
attendance.setup(bot)     # Attendance workflow (export/import CSV)
getids.setup(bot)         # ID export commands
helpcommands.setup(bot)   # Command listing (/ncmd and /acmd)

# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"📌 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")

@bot.event
async def on_member_join(member):
    """Welcome new members with a public announcement."""
    try:
        # Find welcome channel or use first available text channel
        welcome_channel = discord.utils.find(
            lambda c: c.name in ["welcome", "introductions", "general"] and isinstance(c, discord.TextChannel),
            member.guild.channels
        )
        
        if not welcome_channel:
            welcome_channel = next(
                (c for c in member.guild.text_channels if not c.name.startswith(".")
                ), None
            )
        
        if not welcome_channel:
            print(f"⚠️ No suitable channel found for {member.name}")
            return

        embed = discord.Embed(
            title="🎉 New Member Joined!",
            description=f"Welcome {member.mention} to the Guild!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 Quick Setup",
            value=f"**{member.name}**, please change your server nickname to your **In-Game Name (IGN)**:\n\n1. Right-click on your name\n2. Select \"Edit Server Profile\"\n3. Enter your IGN → Save",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Get Started",
            value="• `/ncmd` - View all commands\n• `/items` - See rewards\n• `/points` - Check your balance",
            inline=False
        )
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text="Welcome to the adventure!")
        
        await welcome_channel.send(embed=embed)
        print(f"✅ Welcome message posted for {member.name} in #{welcome_channel.name}")
    except Exception as e:
        print(f"❌ Error posting welcome message: {e}")

# =========================
# RUN BOT
# =========================
bot.run(os.getenv("BOT_TOKEN"))
