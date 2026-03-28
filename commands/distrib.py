import discord
from discord import app_commands
import csv
import random
import io

RARITY_ORDER = {"common":1, "uncommon":2, "rare":3, "epic":4, "legend":5, "mythic":6}
RARITY_EMOJIS = {"common":"⚪", "uncommon":"🟢", "rare":"🔵", "epic":"🔴", "legend":"🟡", "mythic":"🟣"}

def setup(bot):
    @bot.tree.command(name="distribute", description="Fair loot raid distribution - readable")
    @app_commands.describe(participants_file="Names CSV", items_csv="Loot CSV")
    async def distribute_cmd(interaction: discord.Interaction, participants_file: discord.Attachment, items_csv: discord.Attachment):
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Mod only", ephemeral=True)
        
        await interaction.response.defer()
        
        try:
            p_text = (await participants_file.read()).decode(errors='ignore')
            participants = [l.strip() for l in p_text.splitlines() if l.strip()]
            if not participants:
                return await interaction.followup.send("❌ No participants")
            
            i_text = (await items_csv.read()).decode(errors='ignore')
            reader = csv.reader(i_text.splitlines())
            items = []
            for row in reader:
                if len(row) >= 3:
                    name = row[0].strip()
                    qty = int(row[1])
                    rar = row[2]
                    typ = row[3].lower() if len(row) > 3 else "material"
                    if qty > 0:
                        items.append({"name":name, "rarity":rar, "quantity":qty, "type":typ})
            
            if not items:
                return await interaction.followup.send("❌ No loot")
            
            dist = {p:[] for p in participants}
            
            # Equipment fair
            equip = [i for i in items if "equip" in i["type"]]
            for item in sorted(equip, key=lambda x:RARITY_ORDER.get(x["rarity"],0), reverse=True):
                cycle = participants.copy()
                random.shuffle(cycle)
                for i in range(item["quantity"]):
                    dist[cycle[i % len(cycle)]].append(item["name"])
            
            # Materials multi
            mats = [i for i in items if "equip" not in i["type"]]
            for item in sorted(mats, key=lambda x:RARITY_ORDER.get(x["rarity"],0), reverse=True):
                random.shuffle(participants)
                i = 0
                for _ in range(item["quantity"]):
                    dist[participants[i % len(participants)]].append(item["name"])
                    i += 1
            
            # Readable embed - plain text
            embed = discord.Embed(title="RAID LOOT", color=0x00ff00)
            lines = []
            total = sum(i["quantity"] for i in items)
            for p, l in dist.items():
                n = len(l)
                if n:
                    preview = [name[:14] for name in l[:2]]
                    txt = " | ".join(preview)
                    if n > 2:
                        txt += f" +{n-2}"
                    lines.append(f"**{p}** ({n}): {txt}")
                else:
                    lines.append(f"**{p}** (0)")
            
            embed.description = "\n".join(lines[:25])
            if len(lines) > 25:
                embed.add_field(name="...", value="... + more", inline=False)
            embed.set_footer(text=f"Total: {total} items")
            
            # CSV plain names
            out = io.StringIO()
            cw = csv.writer(out)
            cw.writerow(["player", "loot"])
            for p, l in dist.items():
                cw.writerow([p, ", ".join(l)])
            f = discord.File(io.BytesIO(out.getvalue().encode()), "raid_loot.csv")
            
            await interaction.followup.send(embed=embed, file=f)
            
        except Exception as e:
            await interaction.followup.send(f"❌ {str(e)}")


