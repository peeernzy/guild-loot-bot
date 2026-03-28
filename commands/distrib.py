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
        items_csv="items.csv (loot,stock,rarity,type) - equipment/material"
    )
    async def distribute_cmd(interaction: discord.Interaction,
                           participants_file: discord.Attachment,
                           stock_file: discord.Attachment = None):
        # Mod check private
        allowed_roles = {"Moderator", "Elder"}
        if not any(role.name in allowed_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Mod/Elder only", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            # Participants from CSV
            participants_bytes = await participants_file.read()
            participants_text = participants_bytes.decode("utf-8")
            participants_reader = csv.DictReader(io.StringIO(participants_text))
            participants = [row["name"].strip() for row in participants_reader if row.get("name", "").strip()]

            if not participants:
                await interaction.followup.send("❌ **No participants found** ⚠️")
                return

            # Items - prefer stock_file, fallback DB
            items = []
            if stock_file:
                # Custom stock CSV
                items_bytes = await stock_file.read()
                items_text = items_bytes.decode("utf-8")
                items_reader = csv.DictReader(io.StringIO(items_text))
                for row in items_reader:
                    name = row["loot"].strip()
                    rarity = row["rarity"].strip()
                    item_type = row.get("type", "material").strip().lower()
                    try:
                        quantity = int(row["stock"])
                        if name and quantity > 0:
                            items.append({"name": name, "rarity": rarity, "quantity": quantity, "type": item_type})
                    except:
                        pass
            else:
                # Use DB items (name from loot_meta, random quantity 1-stock)
                _, _, _, loot_meta = load_loot_items_from_db()
                for name, meta in loot_meta.items():
                    rarity = meta.get("rarity", "common")
                    stock = meta.get("stock", 1)
                    # Random qty 1-3 for demo
                    qty = random.randint(1, min(3, stock))
                    if qty > 0:
                        items.append({"name": name, "rarity": rarity, "quantity": qty})

            if not items:
                await interaction.followup.send("❌ **No loot available** - DB empty or CSV invalid ⚠️")
                return

            # Round-robin distribution (rarity priority)
            distribution = {p: [] for p in participants}
            # Group by type/priority
            equipment_items = [i for i in items if i.get("type") == "equipment"]
            material_items = [i for i in items if i.get("type") != "equipment"]

            # EQUIPMENT FIRST - strict round robin
            for item in sorted(equipment_items, key=lambda x: rarity_order.get(x["rarity"], 99), reverse=True):
                participants_copy = participants.copy()
                random.shuffle(participants_copy)
                p_index = 0
                for _ in range(item["quantity"]):
                    distribution[participants_copy[p_index % len(participants_copy)]].append(item["name"])
                    p_index += 1

            # MATERIALS - multiple OK, normal round robin
            for item in sorted(material_items, key=lambda x: rarity_order.get(x["rarity"], 99), reverse=True):
                random.shuffle(participants)
                p_index = 0
                for _ in range(item["quantity"]):
                    distribution[participants[p_index]].append(item["name"])
                    p_index = (p_index + 1) % len(participants)

            # PUBLIC RAID EMBED
            embed = discord.Embed(title="🏆 **LOOT DISTRIBUTION** 🎉", color=0xFF4500)
            result_lines = []
            total_loot = sum(item["quantity"] for item in items)
            for player, loot_list in distribution.items():
                count = len(loot_list)
                if count > 0:
                    top_loot = []
                    for item_name in loot_list[:8]:
                        rarity = next((i["rarity"] for i in items if i["name"] == item_name), "common")
                        emoji = rarity_emojis.get(rarity, "⚪")
                        top_loot.append(f"{emoji}`{item_name}`")
                    display = " | ".join(top_loot)
                    if count > 8:
                        display += f" **+{count-8}** 🔥"
                    result_lines.append(f"⚔️ **{player}** `{count}`: {display}")
                else:
                    result_lines.append(f"💀 **{player}** `0`")

            embed.add_field(name="**RAID RESULTS**", value="\n".join(result_lines), inline=False)
            embed.set_footer(text=f"🔥 **{total_loot}** Items | **{len(participants)}** Raiders")

            # CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["player", "loot"])
            for player, loot_list in distribution.items():
                loot_display = [f"{rarity_emojis.get(next((i['rarity'] for i in items if i['name'] == item), ''), '')}{item}" 
                               for item in loot_list]
                writer.writerow([player, "; ".join(loot_display)])
            csv_file = discord.File(io.BytesIO(output.getvalue().encode()), "raid_loot.csv")

            await interaction.followup.send(embed=embed, file=csv_file)

        except Exception as e:
            await interaction.followup.send(f"💥 **Raid Error** `{str(e)}`")


