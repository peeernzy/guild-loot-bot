import discord
from discord import app_commands
import csv
import random
import io

RARITY_ORDER = {"common":1, "uncommon":2, "rare":3, "epic":4, "legend":5, "mythic":6}

def setup(bot):
    @bot.tree.command(name="distribute", description="Raid loot - ALL items listed")
    @app_commands.describe(participants_file="Names CSV", items_csv="Loot CSV")
    async def distribute_cmd(interaction: discord.Interaction, participants_file: discord.Attachment, items_csv: discord.Attachment):
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Mod only", ephemeral=True)
        
        await interaction.response.defer()
        
        try:
            p_text = (await participants_file.read()).decode('utf-8', errors='ignore')
            participants = [l.strip() for l in p_text.splitlines() if l.strip()]
            if not participants:
                return await interaction.followup.send("❌ No participants")
            
            i_text = (await items_csv.read()).decode('utf-8', errors='ignore')
            reader = csv.reader(i_text.splitlines())
            items = []
            for row in reader:
                if len(row) >= 3 and row[0].strip():
                    name = row[0].strip()
                    qty = int(row[1])
                    rar = row[2]
                    typ = row[3].lower() if len(row) > 3 else "material"
                    if qty > 0:
                        items.append({"name":name, "rarity":rar, "quantity":qty, "type":typ})
            
            if not items:
                return await interaction.followup.send("❌ No loot")
            
            dist = {p: [] for p in participants}
            
            equip = [i for i in items if "equip" in i["type"]]
            for item in sorted(equip, key=lambda x: RARITY_ORDER.get(x["rarity"],0), reverse=True):
                cycle = participants.copy()
                random.shuffle(cycle)
                for i in range(item["quantity"]):
                    dist[cycle[i % len(cycle)]].append(item["name"])
            
            mats = [i for i in items if "equip" not in i["type"]]
            for item in sorted(mats, key=lambda x: RARITY_ORDER.get(x["rarity"],0), reverse=True):
                random.shuffle(participants)
                i = 0
                for _ in range(item["quantity"]):
                    dist[participants[i % len(participants)]].append(item["name"])
                    i += 1
            
            total = sum(i["quantity"] for i in items)
            
            # FULL list for each player - multiple messages if needed
            for player, loot_list in dist.items():
                loot_text = ", ".join(loot_list)
                if len(loot_text) > 4000:
                    # Split long lists
                    chunks = [loot_text[i:i+3500] for i in range(0, len(loot_text), 3500)]
                    embed = discord.Embed(title=f"{player} Loot ({len(loot_list)})", color=0x00ff88)
                    embed.description = f"`{chunks[0]}`"
                    await interaction.followup.send(embed=embed)
                    for chunk in chunks[1:]:
                        embed.description = f"`{chunk}`"
                        await interaction.followup.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"{player} Loot ({len(loot_list)})", color=0x00ff88)
                    embed.description = f"`{loot_text}`"
                    await interaction.followup.send(embed=embed)
            
            # CSV summary
            csv_lines = ["Player,Items"]
            for p, l in dist.items():
                csv_lines.append(f'{p},"{",".join(l)}"')
            csv_content = "\n".join(csv_lines)
            csv_file = discord.File(io.BytesIO(csv_content.encode('utf-8')), "raid_loot.csv")
            
            summary_embed = discord.Embed(title="RAID DONE", color=0x00aa00)
            summary_embed.add_field(name="Players", value=len(participants), inline=True)
            summary_embed.add_field(name="Total Loot", value=total, inline=True)
            await interaction.followup.send(embed=summary_embed, file=csv_file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ {str(e)}")



