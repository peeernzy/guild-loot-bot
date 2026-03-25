import io
import json

import discord


def _build_csv_rows(items: list[dict]) -> str:
    lines = ["code,name,cost,rule,aliases"]

    for item in items:
        aliases = "|".join(item.get("aliases", []))
        code = str(item.get("code", "")).replace('"', '""')
        name = str(item.get("name", "")).replace('"', '""')
        cost = str(item.get("cost", ""))
        rule = str(item.get("rule", "")).replace('"', '""')
        aliases = aliases.replace('"', '""')

        lines.append(f'"{code}","{name}","{cost}","{rule}","{aliases}"')

    return "\n".join(lines)


def setup(bot):
    @bot.tree.command(name="exportitems", description="Export the current loot items as a CSV file")
    async def export_items_cmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message(
                "❌ Only Moderators and Elders can export item lists.",
                ephemeral=True
            )
            return

        try:
            with open("loot_items.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            await interaction.response.send_message(
                "❌ `loot_items.json` was not found.",
                ephemeral=True
            )
            return
        except json.JSONDecodeError:
            await interaction.response.send_message(
                "❌ `loot_items.json` is invalid.",
                ephemeral=True
            )
            return

        items = data.get("items", [])
        csv_content = _build_csv_rows(items)
        file_buffer = io.BytesIO(csv_content.encode("utf-8"))

        await interaction.response.send_message(
            "📦 Exported the current loot item list.",
            file=discord.File(file_buffer, filename="loot_items_export.csv"),
            ephemeral=True
        )
