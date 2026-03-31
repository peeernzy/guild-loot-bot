import discord

WELCOME_CHANNEL_ID = 1437365063278137375
WELCOME_IMAGE = "https://i.imgur.com/gYAUbNz.png"  # <-- DIRECT LINK

def setup(bot):

    @bot.event
    async def on_member_join(member):
        try:
            welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)

            if not welcome_channel:
                print(f'⚠️ Welcome channel not found (ID: {WELCOME_CHANNEL_ID})')
                return

            embed = discord.Embed(
                title='🎉 New Member Joined!',
                description=f'Welcome {member.mention} to the Guild!',
                color=discord.Color.green()
            )

            embed.add_field(
                name='📝 Quick Setup',
                value=(
                    f'**{member.name}**, please change your server nickname to your **IGN**:\n\n'
                    '1. Right-click your name\n'
                    '2. Edit Server Profile\n'
                    '3. Enter IGN → Save'
                ),
                inline=False
            )

            embed.add_field(
                name='🎮 Get Started',
                value='• `/ncmd` - View commands\n• `/items` - Rewards\n• `/points` - Balance',
                inline=False
            )

            embed.set_thumbnail(url=member.display_avatar.url)

            # ✅ Only show image inside embed
            embed.set_image(url=WELCOME_IMAGE)

            embed.set_footer(text='Welcome to the adventure!')

            await welcome_channel.send(embed=embed)
            print(f'✅ Welcome message posted for {member.name}')

        except Exception as e:
            print(f'❌ Error posting welcome message: {e}')