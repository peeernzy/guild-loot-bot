import discord
from discord import app_commands
from .loot import loot_aliases, loot_costs
from .utils import remaining_claims

def setup(bot):
    @bot.tree.command(name="items", description="Show loot codes and aliases")
    async def items_cmd(interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎁 Loot Shop",
            description="Earn points from Sindris Island and Clan Sanctuary, then claim your rewards!",
            color=discord.Color.gold()
        )

        emoji_map = {
            "Rare Equipment": "🛡️",
            "Rare Weapon": "🗡️",
            "Rare Materials": "📦",
            "Radiant Enchantment Stone": "✨",
            "Darkening Enchantment Stone": "🌑",
            "Middle Horn": "📯",
            "Lesser Horn": "🎺",
            "Silvarin": "💎",
            "Gwemix Piece Pouch": "🎒",
            "Artisan": "⚒️"
        }

        user_id = interaction.user.id

        # Separate claim vs bid items
        claim_items = []
        bid_items = []

        for code, name in loot_aliases.items():
            if code.isdigit():
                cost = loot_costs.get(name, {"cost": 0, "rule": "No rule"})
                rule = cost.get("rule", "No rule")
                emoji = emoji_map.get(name, "❔")
                points = cost['cost']

                remaining = remaining_claims(user_id, name)
                extra = f"\n📊 Remaining: {remaining}" if remaining is not None else ""

                field_value = f"**Cost:** {points} pts\n**Rule:** {rule}{extra}"

                if "Bidding" in rule:
                    bid_items.append((emoji, code, name, field_value, points))
                else:
                    claim_items.append((emoji, code, name, field_value, points))

        # Add claim items section
        if claim_items:
            embed.add_field(
                name="✅ CLAIM ITEMS",
                value="Fixed price • Use `/claim [code]`",
                inline=False
            )
            for emoji, code, name, field_value, points in sorted(claim_items, key=lambda x: x[4]):
                embed.add_field(
                    name=f"{emoji} [{code}] {name}",
                    value=field_value,
                    inline=True
                )

        # Add bidding items section
        if bid_items:
            embed.add_field(
                name="⚔️ BIDDING ITEMS",
                value="Highest bid wins • Use `/bid [code] [amount]`",
                inline=False
            )
            for emoji, code, name, field_value, points in sorted(bid_items, key=lambda x: x[4], reverse=True):
                embed.add_field(
                    name=f"{emoji} [{code}] {name}",
                    value=field_value,
                    inline=True
                )
        # Add quick reference
        embed.add_field(
            name="🎯 QUICK REFERENCE",
            value="**Earn Points:**\n🟢 Sindris Win: +20\n🟡 Sindris Lose: +10\n🔵 Clan Participated: +15",
            inline=False
        )

        # Aliases section
        aliases = ", ".join([f"`{alias}`" for alias in loot_aliases.keys() if not alias.isdigit()])
        embed.add_field(
            name="🔑 ALIASES",
            value=f"Shortcuts: {aliases}",
            inline=False
        )

        embed.set_footer(text="Use /points to check your balance • /leaderboard for top earners")

        await interaction.response.send_message(embed=embed, ephemeral=True)
