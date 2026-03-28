import discord
from discord import app_commands
import csv
import random
import io

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
    @bot.tree.command(name="distribute", description="Distribute loot fairly from 2 CSVs - PUBLIC")
    @app_commands.describe(
        participants_file="participants.csv (column: name)",
        items_file="items.csv (name,rarity,quantity)"
    )
    async def distribute_cmd(interaction: discord.Interaction,
                           participants_file: discord.Attachment,
                           items_file: discord.Attachment):
        # Mod check (private error)
        allowed_roles = {"Moderator", "Elder"}
        if not any(role.name in allowed_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ **Mod/Elder only** ⚠️", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            # Parse participants
            participants_bytes = await participants_file.read()
            participants_text = participants_bytes.decode("utf-8")
            participants_reader = csv.DictReader(io.StringIO(participants_text))
            participants = [row["name"].strip() for row in participants_reader if row["name"].strip()]

            if not participants:
                await interaction.followup.send("❌ **No participants** - empty CSV? ⚠️")
                return

            # Parse items
            items_bytes = await items_file.read()
            items_text = items_bytes.decode("utf-8")
            items_reader = csv.DictReader(io.StringIO(items_text))
            items = []
            for row in items_reader:
                name = row["name"].strip()
                rarity = row["rarity"].strip()
                try:
                    quantity = int(row["quantity"])
                    if name and quantity > 0:
                        items.append({"name": name, "rarity": rarity, "quantity": quantity})
                except:
                    pass

            if not items:
                await interaction.followup.send("❌ **No valid loot** - check CSV columns ⚠️")
                return

            # Priority round-robin distribution
            distribution = {p: [] for p in participants}
            items_sorted = sorted(items, key=lambda x: rarity_order.get(x["rarity"], 99), reverse=True)

            for item in items_sorted:
                random.shuffle(participants)
                p_index = 0
                for _ in range(item["quantity"]):
                    distribution[participants[p_index]].append(item["name"])
                    p_index = (p_index + 1) % len(participants)

            # GAMER EMBED 🏆
            embed = discord.Embed(title="🏆 **LOOT DISTRIBUTION** 🎉", color=0xFF4500)
            embed.description = "**RAID RESULTS:**\n\n"

            result_lines = []
            total_loot = sum(item["quantity"] for item in items)
            for participant, loot_list in distribution.items():
                count = len(loot_list)
                if count > 0:
                    # Show top 8 with emojis
                    top_loot = []
                    for item_name in loot_list[:8]:
                        item_rarity = next((i["rarity"] for i in items if i["name"] == item_name), "common")
                        emoji = rarity_emojis.get(item_rarity, "⚪")
                        top_loot.append(f"{emoji}`{item_name}`")
                    
                    loot_display = " | ".join(top_loot)
                    if count > 8:
                        loot_display += f" **+{count-8}** 🔥"
                    result_lines.append(f"⚔️ **{participant}** `{count}`: {loot_display}")
                else:
                    result_lines.append(f"💀 **{participant}** `0`")

            embed.add_field(name="**DISTRIBUTED**", value="\n".join(result_lines), inline=False)
            embed.set_footer(text=f"🔥 **{total_loot}** Total Items | Party: **{len(participants)}** Raiders")

            # CSV Export
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["player", "loot"])
            for player, loot_list in distribution.items():
                loot_display = []
                for item_name in loot_list:
                    item_rarity = next((i["rarity"] for i in items if i["name"] == item_name), "")
                    emoji = rarity_emojis.get(item_rarity, "")
                    loot_display.append(f"{emoji}{item_name}")
                writer.writerow([player, "; ".join(loot_display)])
            output.seek(0)
            csv_file = discord.File(io.BytesIO(output.getvalue().encode()), "raid_loot.csv")

            await interaction.followup.send(embed=embed, file=csv_file)

        except Exception as e:
            await interaction.followup.send(f"💥 **Raid Failed** - `{str(e)[:100]}`")
