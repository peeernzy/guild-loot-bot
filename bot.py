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
from commands import points, loot, leaderboard, items, summary, reset, attendance, getids, helpcommands, welcome, goodbye, cls, item_import, item_export, claim, bid, history, setpointlimit, price, transfer, claimwinner

# Register SYNC commands (remove async ones)
points.setup(bot)
loot.setup(bot)
leaderboard.setup(bot)
items.setup(bot)
summary.setup(bot)
reset.setup(bot)
attendance.setup(bot)
getids.setup(bot)
helpcommands.setup(bot)
welcome.setup(bot)
goodbye.setup(bot)
item_export.setup(bot)
claim.setup(bot)
bid.setup(bot)
history.setup(bot)
transfer.setup(bot)
claimwinner.setup(bot)
# ASYNC cogs loaded in on_ready(): cls, item_import, setpointlimit, price

print("📦 Loaded command modules: points, loot, leaderboard, items, summary, reset, attendance, getids, helpcommands, welcome, goodbye, cls, item_import, item_export, claim, bid, history, setpointlimit, price")

from commands.logger import initialize_history
initialize_history()


# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    # Load cogs (async with await, sync without)
    from commands import cls, item_import, setpointlimit, price
    await cls.setup(bot)
    item_import.setup(bot)
    setpointlimit.setup(bot)
    await price.setup(bot)
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"📌 Synced {len(synced)} slash commands: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# =========================
# RUN BOT
# =========================
bot.run(os.getenv("BOT_TOKEN"))
