import io
import json

import discord


def _build_csv_rows(items: list[dict]) -> str:
    lines = ["code,name,cost,rule,stock,rarity"]

    for name_key, details in items:
        code = str(name_key).replace('"', '""')  # dict key as code
        name = str(details.get("name", name_key)).replace('"', '""')
        cost = str(details.get("cost", ""))
        rule = str(details.get("rule", "")).replace('"', '""')
        stock = str(details.get("stock", ""))
        rarity = str(details.get("rarity", "")).replace('"', '""')

        lines.append(f'"{code}","{name}","{cost}","{rule}","{stock}","{rarity}"')

    return "\n".join(lines)


def setup(bot):
    @bot.tree.command(name="expitems", description="Export loot items to CSV (compatible with /impitems)")
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

        items = list(data.items())  # Convert dict items to list for current JSON format {name: {details}}
        csv_content = _build_csv_rows(items)
        file_buffer = io.BytesIO(csv_content.encode("utf-8"))

        await interaction.response.send_message(
            f"📦 Exported **{len(items)}** loot items as CSV.",
            file=discord.File(file_buffer, filename="loot_items_export.csv"),
            ephemeral=True
        )
