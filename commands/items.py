import discord
from discord import app_commands
from .loot import loot_aliases, loot_costs  # import your alias and cost tables
from .utils import remaining_claims        # ✅ import remaining claims tracker

def setup(bot):
    @bot.tree.command(name="items", description="Show loot codes and aliases")
    async def items_cmd(interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 Loot Codes & Aliases",
            description="Use these codes or aliases with `/claim`",
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

        # Show numeric codes with emoji, cost, rule, and remaining claims
        for code, name in loot_aliases.items():
            if code.isdigit():
                cost = loot_costs.get(name, {"cost": 0, "rule": "No rule"})
                emoji = emoji_map.get(name, "❔")

                # ✅ Show remaining claims if item has a weekly limit
                remaining = remaining_claims(user_id, name)
                extra = f"\nRemaining: {remaining}" if remaining is not None else ""

                embed.add_field(
                    name=f"{emoji} {code} → {name}",
                    value=f"Cost: {cost['cost']} pts\nRule: {cost['rule']}{extra}",
                    inline=False
                )

        # Aliases section
        aliases = ", ".join([alias for alias in loot_aliases.keys() if not alias.isdigit()])
        embed.add_field(
            name="🔑 Aliases",
            value=f"You can also use: {aliases}",
            inline=False
        )

        await interaction.response.send_message(embed=embed)
