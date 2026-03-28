import discord
from discord import app_commands
import csv
import random
import io

# Rarity priority and emojis
RARITY_ORDER = {"common":1, "uncommon":2, "rare":3, "epic":4, "legend":5, "mythic":6}
RARITY_EMOJIS = {"common":"⚪", "uncommon":"🟢", "rare":"🔵", "epic":"🔴", "legend":"🟡", "mythic":"🟣"}

def setup(bot):
    @bot.tree.command(name="distribute", description="🎲 Fair loot distribution for raids (Mod/Elder)")
    @app_commands.describe(
        participants_file="CSV or TXT with raider names (one per line)",
        items_csv="CSV: loot,stock,rarity,type (header optional)"
    )
    async def distribute_cmd(interaction: discord.Interaction, participants_file: discord.Attachment, items_csv: discord.Attachment):
        # Permission check
        if not any(role.name in {"Moderator", "Elder"} for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Moderator/Elder only", ephemeral=True)
        
        await interaction.response.defer()
        
        try:
            # ========== PARSE PARTICIPANTS ==========
            p_bytes = await participants_file.read()
            p_text = p_bytes.decode('utf-8', errors='ignore')
            participants = [line.strip() for line in p_text.splitlines() if line.strip()]
            
            if len(participants) == 0:
                return await interaction.followup.send("❌ **No participants found**\nAdd names (one per line)")
            
            # ========== PARSE ITEMS ==========
            i_bytes = await items_csv.read()
            i_text = i_bytes.decode('utf-8', errors='ignore')
            items = []
            
            reader = csv.reader(i_text.splitlines())
            row_num = 0
            for row in reader:
                row_num += 1
                if len(row) < 3 or not row[0].strip():
                    continue  # Skip empty rows
                
                try:
                    name = row[0].strip()
                    qty = int(row[1].strip())
                    rarity = row[2].strip()
                    item_type = row[3].strip().lower() if len(row) > 3 else "material"
                    
                    if qty > 0 and name:
                        items.append({
                            "name": name,
                            "rarity": rarity,
                            "quantity": qty, 
                            "type": item_type
                        })
                except (ValueError, IndexError):
                    continue  # Skip invalid rows
            
            if len(items) == 0:
                return await interaction.followup.send("❌ **No valid loot found**\nFormat: `MIDDLE HORN,3,rare,consumable`")
            
            # ========== FAIR DISTRIBUTION ==========
            distribution = {player: [] for player in participants}
            
            # 1. EQUIPMENT - STRICT 1 PER PLAYER
            equipment = [it for it in items if 'equip' in it["type"]]
            for item in sorted(equipment, key=lambda x: RARITY_ORDER.get(x["rarity"], 0), reverse=True):
                cycle = participants.copy()
                random.shuffle(cycle)
                for i in range(item["quantity"]):
                    player = cycle[i % len(cycle)]
                    distribution[player].append(item["name"])
            
            # 2. MATERIALS - NORMAL ROUND ROBIN (multi OK)
            materials = [it for it in items if 'equip' not in it["type"]]
            for item in sorted(materials, key=lambda x: RARITY_ORDER.get(x["rarity"], 0), reverse=True):
                random.shuffle(participants)
                i = 0
                for _ in range(item["quantity"]):
                    player = participants[i % len(participants)]
                    distribution[player].append(item["name"])
                    i += 1
            
            # ========== PUBLIC EMBED ==========
            embed = discord.Embed(title="🏆 **RAID LOOT DISTRIBUTION**", color=discord.Color.green())
            
            # Results table
            result_lines = []
            total_loot = sum(item["quantity"] for item in items)
            
            for player, player_loot in distribution.items():
                count = len(player_loot)
                if count > 0:
                    # Show top 4 items with emojis
                    preview_loot = []
                    for loot_name in player_loot[:4]:
                        loot_rarity = next((it["rarity"] for it in items if it["name"] == loot_name), "common")
                        emoji = RARITY_EMOJIS.get(loot_rarity, "⚪")
                        preview_loot.append(f"{emoji} `{loot_name}`")
                    
                    loot_display = " | ".join(preview_loot)
                    if count > 4:
                        loot_display += f" **+{count - 4} more**"
                    
                    result_lines.append(f"⚔️ **{player}** `({count})` {loot_display}")
                else:
                    result_lines.append(f"💀 **{player}** `(0)`")
            
            embed.add_field(
                name=f"**RAID RESULTS** ({len(participants)} raiders)",
                value="\n".join(result_lines),
                inline=False
            )
            
            embed.set_footer(text=f"📦 Total loot distributed: {total_loot} items")
            
            # ========== DOWNLOAD CSV ==========
            output_buffer = io.StringIO()
            csv_writer = csv.writer(output_buffer)
            csv_writer.writerow(["player", "loot_items"])
            
            for player, player_loot in distribution.items():
                loot_list = []
                for loot_name in player_loot:
                    loot_rarity = next((it["rarity"] for it in items if it["name"] == loot_name), "common")
                    emoji = RARITY_EMOJIS.get(loot_rarity, "")
                    loot_list.append(f"{emoji}{loot_name}")
                csv_writer.writerow([player, "; ".join(loot_list)])
            
            csv_bytes = output_buffer.getvalue().encode('utf-8')
            loot_file = discord.File(io.BytesIO(csv_bytes), filename="raid_loot.csv")
            
            await interaction.followup.send(embed=embed, file=loot_file)
            
        except Exception as error:
            await interaction.followup.send(f"💥 **Raid failed** - `{str(error)[:150]}`")


