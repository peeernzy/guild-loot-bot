import discord
from datetime import datetime, timezone

GOODBYE_CHANNEL_ID = 1486238687300681769

# Optional banner (replace with your own image)
BANNER_URL = "https://i.imgur.com/8Km9tLL.png"

def setup(bot):

    @bot.event
    async def on_member_remove(member):
        try:
            channel = bot.get_channel(GOODBYE_CHANNEL_ID)

            if not channel:
                print(f"⚠️ Goodbye channel not found (ID: {GOODBYE_CHANNEL_ID})")
                return

            # 👤 Smart name
            if member.display_name == member.name:
                name_text = f"**{member.name}**"
            else:
                name_text = f"**{member.display_name}** ({member.name})"

            # 🎨 Role color (fallback if default)
            color = member.top_role.color if member.top_role.color.value != 0 else discord.Color.dark_gray()

            # 🎭 Roles (clean + limit)
            roles = [role.mention for role in member.roles if role.name != "@everyone"]
            if roles:
                roles_text = " ".join(roles[:10])  # limit to 10 roles
                if len(roles) > 10:
                    roles_text += f" +{len(roles) - 10} more"
            else:
                roles_text = "`No roles`"

            # 📊 Member count
            member_count = member.guild.member_count

            # 🕒 Discord timestamps
            joined_ts = int(member.joined_at.replace(tzinfo=timezone.utc).timestamp()) if member.joined_at else None
            created_ts = int(member.created_at.replace(tzinfo=timezone.utc).timestamp())

            joined_text = f"<t:{joined_ts}:F>" if joined_ts else "`Unknown`"
            created_text = f"<t:{created_ts}:F>"

            # 🚨 Account check
            now = datetime.now(timezone.utc)
            account_age_days = (now - member.created_at).days

            if account_age_days < 7:
                status = "🚨 **New Account (Possible Alt)**"
            elif account_age_days < 30:
                status = "⚠️ **Recently Created Account**"
            else:
                status = "✔️ **Trusted Account**"

            # 💎 Embed
            embed = discord.Embed(
                description=(
                    f"╭・👋 **Member Left**\n"
                    f"╰・{member.mention} has left the server\n\n"
                    f"╭・👤 **User Info**\n"
                    f"╰・{name_text}\n\n"
                    f"╭・📅 **Timeline**\n"
                    f"├ Joined: {joined_text}\n"
                    f"╰ Created: {created_text}\n\n"
                    f"╭・🎭 **Roles**\n"
                    f"╰・{roles_text}\n\n"
                    f"╭・📊 **Server Stats**\n"
                    f"├ Members: **{member_count}**\n"
                    f"╰ Status: {status}"
                ),
                color=color
            )

            # 🖼️ Visuals
            embed.set_thumbnail(
                url=member.avatar.url if member.avatar else member.default_avatar.url
            )

            embed.set_image(url=BANNER_URL)

            embed.set_footer(text=f"{member.guild.name} • Goodbye System")
            embed.timestamp = datetime.now(timezone.utc)

            await channel.send(embed=embed)

            print(f"💎 Premium goodbye sent for {member.display_name}")

        except Exception as e:
            print(f"❌ Error: {e}")