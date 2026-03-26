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
from commands import points, loot, leaderboard, items, summary, reset, attendance, getids, helpcommands, welcome, goodbye, cls, item_import, item_export, claim, bid, history

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
item_import.setup(bot)    # CSV loot item import command
item_export.setup(bot)    # CSV loot item export command
claim.setup(bot)          # Claim command
bid.setup(bot)            # Bid command
history.setup(bot)        # History command
coins.setup(bot)           # Coins command
setpointlimit.setup(bot)   # Set point limit

print("📦 Loaded command modules: points, loot, leaderboard, items, summary, reset, attendance, getids, helpcommands, welcome, goodbye, cls, item_import, item_export, claim, bid, history, coins, setpointlimit")


# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        registered = [cmd.name for cmd in bot.tree.get_commands()]
        print(f"🧾 Registered commands before sync ({len(registered)}): {registered}")
        synced = await bot.tree.sync()
        print(f"📌 Synced {len(synced)} slash commands: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# =========================
# RUN BOT
# =========================
bot.run(os.getenv("BOT_TOKEN"))
