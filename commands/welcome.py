import discord

# Channel IDs - hardcoded to avoid confusion
WELCOME_CHANNEL_ID = 1437365063278137375
GOODBYE_CHANNEL_ID = 1486238687300681769

def setup(bot):
    @bot.event
    async def on_member_join(member):
        """Welcome new members with a public announcement."""
        try:
            welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
            
            if not welcome_channel:
                print(f"⚠️ Welcome channel not found (ID: {WELCOME_CHANNEL_ID})")
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
            print(f"✅ Welcome message posted for {member.name}")
        except Exception as e:
            print(f"❌ Error posting welcome message: {e}")
    
    @bot.event
    async def on_member_remove(member):
        """Say goodbye to members who leave."""
        try:
            goodbye_channel = bot.get_channel(GOODBYE_CHANNEL_ID)
            
            if not goodbye_channel:
                print(f"⚠️ Goodbye channel not found (ID: {GOODBYE_CHANNEL_ID})")
                return
            
            embed = discord.Embed(
                title="👋 Member Left",
                description=f"{member.mention} ({member.name}) has left the Guild.",
                color=discord.Color.from_rgb(128, 128, 128)
            )
            
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.set_footer(text="Safe travels!")
            
            await goodbye_channel.send(embed=embed)
            print(f"✅ Goodbye message posted for {member.name}")
        except Exception as e:
            print(f"❌ Error posting goodbye message: {e}")
