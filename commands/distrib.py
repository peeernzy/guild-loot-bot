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
    @bot.tree.command(name="distribute", description="Distribute loot fairly - PUBLIC (Mod/Elder)")
    @app_commands.describe(
        participants_file="participants.csv - one name per line",
        items_csv="items.csv (loot,stock,rarity,type)"
    )
    async def distribute_cmd(interaction: discord.Interaction,
                           participants_file: discord.Attachment,
                           items_csv: discord.Attachment):
        allowed_roles = {"Moderator", "Elder"}
        if not any(role.name in allowed_roles for role in interaction.user.roles):
            await interaction.response.send_message("❌ Mod/Elder only", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            # PARTICIPANTS - one name per line, auto parse
            participants_bytes = await participants_file.read()
            participants_text = participants_bytes.decode("utf-8")
            participants = [line.strip() for line in participants_text.splitlines() if line.strip()]

            if len(participants) < 1:
                await interaction.followup.send("❌ **No participants** - add names to CSV")
                return

            # ITEMS CSV - flexible header
            items_bytes = await items_csv.read()
            items_text = items_bytes.decode("utf-8").strip()
            items = []
            
            # Try DictReader first (header row), fallback positional
            try:
                items_reader = csv.DictReader(io.StringIO(items_text))
                for row in items_reader:
                    name = row.get("loot", row.get("name", "")).strip()
                    try:
                        qty = int(row.get("stock", row.get("quantity", 1)))
                        rar = row.get("rarity", "common").strip()
                        typ = row.get("type", "material").strip().lower()
                        if name and qty > 0:
                            items.append({"name": name, "rarity": rar, "quantity": qty, "type": typ})
                    except ValueError:
                        continue
            except:
                # Positional fallback (no header)
                lines = items_text.splitlines()
                if lines:
                    reader = csv.reader(lines)
                    for row in reader:
                        if len(row) >= 3:
                            name, qty_str, rar = row[0].strip(), row[1].strip(), row[2].strip()
                            typ = row[3].strip().lower() if len(row) > 3 else "material"
                            try:
                                qty = int(qty_str)
                                if name and qty > 0:
                                    items.append({"name": name, "rarity": rar, "quantity": qty, "type": typ})
                            except ValueError:
                                continue

            if not items:
                await interaction.followup.send("❌ **No loot** - check CSV format")
                return

            # DISTRIBUTION
            distribution = {p: [] for p in participants}
            
            # EQUIPMENT PRIORITY
            equip = [i for i in items if i["type"] == "equipment"]
            for item in sorted(equip, key=lambda x: rarity_order.get(x["rarity"], 0), reverse=True):
                cycle = participants.copy()
                random.shuffle(cycle)
                for i in range(item["quantity"]):
                    distribution[cycle[i % len(cycle)]].append(item["name"])

            # MATERIALS normal
            mats = [i for i in items if i["type"] != "equipment"]
            for item in sorted(mats, key=lambda x: rarity_order.get(x["rarity"], 0), reverse=True):
                random.shuffle(participants)
                idx = 0
                for _ in range(item["quantity"]):
                    distribution[participants[idx % len(participants)]].append(item["name"])
                    idx += 1

            # PUBLIC EMBED
            embed = discord.Embed(title="🏆 **RAID LOOT** 🎉", color=0x00FF00)
            lines = []
            total_loot = sum(i["quantity"] for i in items)
            for p, loot in distribution.items():
                cnt = len(loot)
                if cnt:
                    preview = []
                    for name in loot[:8]:
                        r = next((i["rarity"] for i in items if i["name"] == name), "common")
                        preview.append(f'{rarity_emojis.get(r,"⚪")}`{name}`')
                    txt = " | ".join(preview)
                    if cnt > 8: txt += f" **+{cnt-8}**"
                    lines.append(f"⚔️ **{p}** ({cnt}): {txt}")
                else:
                    lines.append(f"💀 **{p}** (0)")
            
            embed.add_field(name=f"**PARTY LOOT** ({len(participants)} raiders)", value="\n".join(lines), inline=False)
            embed.set_footer(text=f"Total items: {total_loot}")

            # CSV OUTPUT
            out = io.StringIO()
            w = csv.writer(out)
            w.writerow(["player", "items"])
            for p, loot in distribution.items():
                w.writerow([p, "; ".join([f'{rarity_emojis.get(next((i["rarity"] for i in items if i["name"] == name),"")}{name}' for name in loot])])
            file = discord.File(io.BytesIO(out.getvalue().encode()), "raid_results.csv")
            
            await interaction.followup.send(embed=embed, file=file)

        except Exception as e:
            await interaction.followup.send(f"💥 **Failed** `{str(e)}`")


