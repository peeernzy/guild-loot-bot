import discord

# Channel ID - hardcoded to avoid confusion
GOODBYE_CHANNEL_ID = 1486238687300681769

def setup(bot):
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
