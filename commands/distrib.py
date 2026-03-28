import discord
from discord import app_commands
import csv
import random
import io
from commands.items_db import load_loot_items_from_db

rarity_order = {
    "common": 1,
    "uncommon": 2,
    "rare": 3,
    "epic": 4,
    "legend": 5,
    "mythic": 6
}

rarity_emojis = {
    "common": "⚪",
    "uncommon": "🟢",
    "rare": "🔵",
    "epic": "🔴",
    "legend": "🟡",
    "mythic": "🟣"
}

def setup(bot):
    @bot.tree.command(name="distribute", description="Distribute loot fairly - PUBLIC (Mod/Elder)")
    @app_commands.describe(
        participants_file="participants.csv (name column)",
        items_csv="items.csv (loot,stock,rarity,type=equipment/material)"
    )
    async def distribute_cmd(interaction: discord.Interaction,
                           participants_file: discord.Attachment,
                           items_csv: discord.Attachment):
        # Mod check private
        allowed_roles = {"Moderator", "Elder"}
        if not any(role.name in allowed_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Mod/Elder only", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            # Participants CSV
            participants_bytes = await participants_file.read()
            participants_text = participants_bytes.decode("utf-8")
            participants_reader = csv.DictReader(io.StringIO(participants_text))
            participants = [row["name"].strip() for row in participants_reader if row.get("name", "").strip()]

            if not participants:
                await interaction.followup.send("❌ No participants found")
                return

            # Items CSV (YOUR FORMAT)
            items_bytes = await items_csv.read()
            items_text = items_bytes.decode("utf-8")
            items_reader = csv.DictReader(io.StringIO(items_text))
            items = []
            for row in items_reader:
                name = row["loot"].strip()
                rarity = row["rarity"].strip()
                item_type = row.get("type", "material").strip().lower()
                try:
                    quantity = int(row["stock"])
                    if name and quantity > 0:
                        items.append({"name": name, "rarity": rarity, "quantity": quantity, "type": item_type})
                except ValueError:
                    pass  # Skip bad rows

            if not items:
                await interaction.followup.send("❌ No valid loot in CSV")
                return

            # DISTRIBUTION LOGIC
            distribution = {p: [] for p in participants}

            # 1. EQUIPMENT first - STRICT fair round-robin
            equipment = [i for i in items if i["type"] == "equipment"]
            for item in sorted(equipment, key=lambda x: rarity_order.get(x["rarity"], 99), reverse=True):
                players_cycle = participants.copy()
                random.shuffle(players_cycle)
                for q in range(item["quantity"]):
                    player = players_cycle[q % len(players_cycle)]
                    distribution[player].append(item["name"])

            # 2. MATERIALS - normal round-robin (multi OK)
            materials = [i for i in items if i["type"] != "equipment"]
            for item in sorted(materials, key=lambda x: rarity_order.get(x["rarity"], 99), reverse=True):
                random.shuffle(participants)
                p_index = 0
                for _ in range(item["quantity"]):
                    distribution[participants[p_index]].append(item["name"])
                    p_index = (p_index + 1) % len(participants)

            # RAID EMBED PUBLIC
            embed = discord.Embed(title="🏆 **LOOT DROP COMPLETE** 🎉", color=0xFF4500)
            result_lines = []
            total_items = sum(item["quantity"] for item in items)
            for player, loot_items in distribution.items():
                count = len(loot_items)
                if count > 0:
                    display_items = []
                    for item_name in loot_items[:10]:
                        item_rarity = next((i["rarity"] for i in items if i["name"] == item_name), "common")
                        emoji = rarity_emojis.get(item_rarity, "⚪")
                        display_items.append(f"{emoji}`{item_name}`")
                    loot_str = " | ".join(display_items)
                    if count > 10:
                        loot_str += f" **+{count-10}** 🔥"
                    result_lines.append(f"⚔️ **{player}** `{count}`: {loot_str}")
                else:
                    result_lines.append(f"💀 **{player}** `0`")

            embed.add_field(name="**RAID RESULTS**", value="\n".join(result_lines), inline=False)
            embed.set_footer(text=f"🔥 **{total_items}** Total Loot | Party: **{len(participants)}**")

            # CSV Export
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["player", "loot"])
            for player, loot_items in distribution.items():
                formatted_loot = []
                for item_name in loot_items:
                    item_rarity = next((i["rarity"] for i in items if i["name"] == item_name), "")
                    emoji = rarity_emojis.get(item_rarity, "")
                    formatted_loot.append(f"{emoji}{item_name}")
                writer.writerow([player, "; ".join(formatted_loot)])
            csv_data = output.getvalue().encode()
            csv_file = discord.File(io.BytesIO(csv_data), "raid_loot.csv")

            await interaction.followup.send(embed=embed, file=csv_file)

        except Exception as e:
            await interaction.followup.send(f"💥 **Raid Failed** - `{str(e)[:100]}`")


