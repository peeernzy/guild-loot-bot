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
    """Welcome new members and ask them to set their IGN nickname."""
    try:
        embed = discord.Embed(
            title="🎉 Welcome to the Guild!",
            description=f"Hello {member.mention}, welcome to our community!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 Please Set Your Nickname",
            value="Change your server nickname to your **In-Game Name (IGN)** so we can identify you properly.\n\n**How to:**\n1. Right-click on your name in the server\n2. Select \"Edit Server Profile\"\n3. Enter your IGN in the nickname field\n4. Click \"Save\"",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Get Started",
            value="Once your nickname is set, use these commands:\n• `/ncmd` - View all available commands\n• `/items` - See loot and rewards\n• `/points` - Check your points balance",
            inline=False
        )
        
        embed.add_field(
            name="❓ Need Help?",
            value="Ask any moderator or Elder if you have questions!",
            inline=False
        )
        
        embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else "")
        embed.set_footer(text="Welcome to the adventure!")
        
        await member.send(embed=embed)
        print(f"✅ Welcome message sent to {member.name}")
    except discord.Forbidden:
        print(f"⚠️ Could not send DM to {member.name} (DMs disabled)")
    except Exception as e:
        print(f"❌ Error sending welcome message: {e}")

# =========================
# RUN BOT
# =========================
bot.run(os.getenv("BOT_TOKEN"))
