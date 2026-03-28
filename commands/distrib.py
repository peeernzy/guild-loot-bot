import discord
from discord import app_commands
import csv
import random
import io

rarity_order = {"common":1,"uncommon":2,"rare":3,"epic":4,"legend":5,"mythic":6}
rarity_emojis = {"common":"⚪","uncommon":"🟢","rare":"🔵","epic":"🔴","legend":"🟡","mythic":"🟣"}

def setup(bot):
    @bot.tree.command(name="distribute", description="Distribute loot raid - PUBLIC")
    @app_commands.describe(participants_file="Raiders CSV (names)", items_csv="Loot CSV (loot,stock,rarity,type)")
    async def distribute_cmd(interaction: discord.Interaction, participants_file: discord.Attachment, items_csv: discord.Attachment):
        if not any(r.name in {"Moderator","Elder"} for r in interaction.user.roles):
            await interaction.response.send_message("❌ Mod only", ephemeral=True)
            return
        await interaction.response.defer()
        try:
            # Participants
            p_data = await participants_file.read()
            p_text = p_data.decode("utf-8")
            participants = [line.strip() for line in p_text.splitlines() if line.strip()]
            if not participants:
                await interaction.followup.send("❌ No participants")
                return

            # Items flexible parse
            i_data = await items_csv.read()
            i_text = i_data.decode("utf-8")
            items = []
            reader = csv.DictReader(i_text.splitlines())
            for row in reader:
                name = row.get("loot","").strip()
                qty_str = row.get("stock","0")
                rar = row.get("rarity","common").strip()
                typ = row.get("type","material").lower().strip()
                try:
                    qty = int(qty_str)
                    if name and qty > 0:
                        items.append({"name":name, "rarity":rar, "quantity":qty, "type":typ})
                except:
                    pass
            if not items:
                await interaction.followup.send("❌ No loot")
                return

            # Distribute
            dist = {p:[] for p in participants}
            
            # Equipment fair
            equip = [i for i in items if i["type"]=="equipment"]
            for item in sorted(equip, key=lambda x:rarity_order.get(x["rarity"],0), reverse=True):
                cycle = participants[:]
                random.shuffle(cycle)
                for j in range(item["quantity"]):
                    dist[cycle[j % len(cycle)]].append(item["name"])

            # Materials
            mats = [i for i in items if i["type"]!="equipment"]
            for item in sorted(mats, key=lambda x:rarity_order.get(x["rarity"],0), reverse=True):
                random.shuffle(participants)
                j = 0
                for _ in range(item["quantity"]):
                    dist[participants[j % len(participants)]].append(item["name"])
                    j += 1

            # Embed
            embed = discord.Embed(title="🏆 RAID LOOT", color=0x00ff00)
            lines = []
            total = sum(i["quantity"] for i in items)
            for p, l in dist.items():
                n = len(l)
                if n:
                    preview = []
                    for name in l[:5]:
                        r = next((it["rarity"] for it in items if it["name"]==name), "common")
                        preview.append(rarity_emojis.get(r,"⚪") + name)
                    txt = " | ".join(preview)
                    if n > 5: txt += f" +{n-5}"
                    lines.append(f"**{p}** ({n}): {txt}")
                else:
                    lines.append(f"**{p}** (0)")
            embed.description = "\n".join(lines)
            embed.set_footer(text=f"Total: {total} | Party: {len(participants)}")

            # CSV
            out = io.StringIO()
            cw = csv.writer(out)
            cw.writerow(["player","loot"])
            for p, l in dist.items():
                cw.writerow([p, ", ".join(l)])
            f = discord.File(io.BytesIO(out.getvalue().encode()), "raid_loot.csv")

            await interaction.followup.send(embed=embed, file=f)
        except Exception as e:
            await interaction.followup.send(f"❌ **Error**: {str(e)}")


