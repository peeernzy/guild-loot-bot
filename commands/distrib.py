import discord
from discord import app_commands
import csv
import random
import io

# Rarity config
RARITY_ORDER = {"common":1, "uncommon":2, "rare":3, "epic":4, "legend":5, "mythic":6}
RARITY_EMOJIS = {"common":"⚪", "uncommon":"🟢", "rare":"🔵", "epic":"🔴", "legend":"🟡", "mythic":"🟣"}

def setup(bot):
    @bot.tree.command(name="distribute", description="🎲 Fair loot raid distribution")
    @app_commands.describe(
        participants_file="Raider names CSV/TXT (1 per line)",
        items_csv="Loot CSV: loot,stock,rarity,type"
    )
    async def distribute_cmd(interaction: discord.Interaction, participants_file: discord.Attachment, items_csv: discord.Attachment):
        # Mod check
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Moderator only", ephemeral=True)
        await interaction.response.defer()
        
        try:
            # Parse participants
            p_text = (await participants_file.read()).decode('utf-8', errors='ignore')
            participants = [line.strip() for line in p_text.splitlines() if line.strip()]
            if not participants:
                return await interaction.followup.send("❌ No participants - add names 1 per line")
            
            # Parse items CSV
            i_text = (await items_csv.read()).decode('utf-8', errors='ignore')
            reader = csv.reader(i_text.splitlines())
            items = []
            for row in reader:
                if len(row) >= 3 and row[0].strip():
                    name = row[0].strip()
                    try:
                        qty = int(row[1])
                        rar = row[2]
                        typ = row[3].lower() if len(row) > 3 else "material"
                        if qty > 0:
                            items.append({"name":name, "rarity":rar, "quantity":qty, "type":typ})
                    except ValueError:
                        continue
            
            if not items:
                return await interaction.followup.send("❌ No loot - format: `NAME,QTY,RARITY,TYPE`")
            
            # Distribution
            dist = {p: [] for p in participants}
            
            # Equipment (fair 1 per player)
            equip = [i for i in items if "equip" in i["type"]]
            for item in sorted(equip, key=lambda x:RARITY_ORDER.get(x["rarity"],0), reverse=True):
                cycle = participants.copy()
                random.shuffle(cycle)
                for i in range(item["quantity"]):
                    dist[cycle[i % len(cycle)]].append(item["name"])
            
            # Materials (multi OK)
            mats = [i for i in items if "equip" not in i["type"]]
            for item in sorted(mats, key=lambda x:RARITY_ORDER.get(x["rarity"],0), reverse=True):
                random.shuffle(participants)
                i = 0
                for _ in range(item["quantity"]):
                    dist[participants[i % len(participants)]].append(item["name"])
                    i += 1
            
            # Embed (readable - 2 items preview)
            embed = discord.Embed(title="🏆 **RAID LOOT**", color=0x00ff00)
            lines = []
            total_loot = sum(i["quantity"] for i in items)
            
            for player, loot_list in dist.items():
                count = len(loot_list)
                if count:
                    preview = []
                    for name in loot_list[:2]:
                        r = next((it["rarity"] for it in items if it["name"]==name), "common")
                        preview.append(RARITY_EMOJIS.get(r, "⚪") + name[:10])
                    txt = " | ".join(preview)
                    if count > 2:
                        txt += f" **+{count-2}**"
                    lines.append(f"**{player}** ({count}): {txt}")
                else:
                    lines.append(f"**{player}** (0)")
            
            embed.description = "\n".join(lines[:25])  # Discord limit safe
            if len(lines) > 25:
                embed.add_field(name="...", value=f"... +{len(lines)-25} more", inline=False)
            embed.set_footer(text=f"Total items: {total_loot}")
            
            # CSV
            out = io.StringIO()
            cw = csv.writer(out)
            cw.writerow(["player", "items"])
            for p, l in dist.items():
                cw.writerow([p, ", ".join(l)])
            csv_file = discord.File(io.BytesIO(out.getvalue().encode()), "raid_loot.csv")
            
            await interaction.followup.send(embed=embed, file=csv_file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ **Error**: `{str(e)}`")


