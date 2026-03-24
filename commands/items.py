import discord
from discord import app_commands
from .loot import loot_aliases, loot_costs
from .utils import remaining_claims

def setup(bot):
    @bot.tree.command(name="items", description="Show loot codes and aliases")
    async def items_cmd(interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 Loot Codes & Aliases",
            description="Use `/claim` for fixed-cost items and `/bid` for bidding items",
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

                remaining = remaining_claims(user_id, name)
                extra = f"\nRemaining: {remaining}" if remaining is not None else ""

                field_value = f"Cost: {cost['cost']} pts\nRule: {rule}{extra}"

                if rule.startswith("Bidding"):
                    bid_items.append((emoji, code, name, field_value))
                else:
                    claim_items.append((emoji, code, name, field_value))

        # Add claim items section
        embed.add_field(
            name="✅ Claim Items",
            value="Use `/claim` for these",
            inline=False
        )
        for emoji, code, name, field_value in claim_items:
            embed.add_field(
                name=f"{emoji} {code} → {name}",
                value=field_value,
                inline=False
            )

        # Add bidding items section
        embed.add_field(
            name="⚔️ Bidding Items",
            value="Use `/bid` for these",
            inline=False
        )
        for emoji, code, name, field_value in bid_items:
            embed.add_field(
                name=f"{emoji} {code} → {name}",
                value=field_value,
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
