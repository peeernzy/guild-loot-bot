import discord
from discord import app_commands
from .loot import claim_aliases, bid_aliases, loot_costs, loot_meta
from .utils import remaining_claims

def setup(bot):
    @bot.tree.command(name="items", description="Show loot codes and aliases")
    async def items_cmd(interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎁 Loot Shop",
            description="Earn points from **Sindri's Island** and **Clan Sanctuary**, then claim your rewards!",
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
            "Silvarin (Bundle)": "💎",
            "Gwemix Piece Pouch": "🎒",
            "Artisan": "⚒️",
            "Enchantment Tome Skill (White)": "📖",
            "Enchantment Tome Skill (Green)": "📗",
            "Enchantment Tome Skill (Rare)": "📘",
            "Soul-Uncommon (Green)": "🟢",
            "Soul-Rare (Blue)": "🔵"
        }

        user_id = interaction.user.id

        # Separate claim vs bid items
        claim_items = []
        bid_items = []

        seen_items = set()

        for alias_map, is_bidding in ((claim_aliases, False), (bid_aliases, True)):
            for code, name in alias_map.items():
                if not code.isdigit() or name in seen_items:
                    continue

                seen_items.add(name)
                cost = loot_costs.get(name, {"cost": 0, "rule": "No rule"})
                rule = cost.get("rule", "No rule")
                emoji = emoji_map.get(name, "❔")
                points = cost["cost"]
                pt_str = "pt" if points == 1 else "pts"

                remaining = remaining_claims(user_id, name)
                extra = f"\n📊 Remaining: {remaining}" if remaining is not None else ""

                source_code = loot_meta.get(name, {}).get("source_code", code)
                field_value = f"**Cost:** {points} {pt_str}\n**Rule:** {rule}{extra}"

                if is_bidding:
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
            for index, (emoji, code, name, field_value, points) in enumerate(sorted(claim_items, key=lambda x: x[4]), start=1):
                embed.add_field(
                    name=f"{emoji} [{index}] {name}",
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
            for index, (emoji, code, name, field_value, points) in enumerate(sorted(bid_items, key=lambda x: x[4], reverse=True), start=1):
                embed.add_field(
                    name=f"{emoji} [{index}] {name}",
                    value=field_value,
                    inline=True
                )
        # Add quick reference
        embed.add_field(
            name="🎯 QUICK REFERENCE",
            value="**Earn Points:**\n🟢 **Sindri's Island** Win: +20\n🟡 **Sindri's Island** Lose: +10\n🔵 **Clan Sanctuary** Participated: +15",
            inline=False
        )

        # Aliases section
        alias_names = sorted({alias for alias in list(claim_aliases.keys()) + list(bid_aliases.keys()) if not alias.isdigit()})
        aliases = ", ".join([f"`{alias}`" for alias in alias_names])
        embed.add_field(
            name="🔑 ALIASES",
            value=f"Shortcuts: {aliases}",
            inline=False
        )

        embed.set_footer(text="Use /points to check your balance • /leaderboard for top earners")

        await interaction.response.send_message(embed=embed, ephemeral=True)

