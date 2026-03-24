import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Import all command modules
from commands import points, loot, leaderboard, items, summary, reset

points.setup(bot)
loot.setup(bot)
leaderboard.setup(bot)
items.setup(bot)
summary.setup(bot)
reset.setup(bot)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)

bot.run(os.getenv("BOT_TOKEN"))
