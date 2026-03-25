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
from commands import points, loot, leaderboard, items, summary, reset, attendance, getids, helpcommands, welcome, goodbye, cls

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
welcome.setup(bot)        # Welcome messages for new members
goodbye.setup(bot)        # Goodbye messages for members leaving
cls.setup(bot)            # Channel cleanup command

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

# =========================
# RUN BOT
# =========================
bot.run(os.getenv("BOT_TOKEN"))
