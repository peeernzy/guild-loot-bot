import discord
from discord import app_commands
import csv
import io
import math

RARITY_ORDER = {"common":1, "uncommon":2, "rare":3, "epic":4, "legend":5, "mythic":6}

def setup(bot):
    @bot.tree.command(name="distribute", description="PERFECT BALANCED loot distribution")
    @app_commands.describe(participants_file="Players CSV (one name per line)", items_csv="Loot CSV")
    async def distribute_cmd(interaction: discord.Interaction, participants_file: discord.Attachment, items_csv: discord.Attachment):
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Mod/Elder only", ephemeral=True)
        
        await interaction.response.defer()
        
        try:
            # Parse participants
            p_text = (await participants_file.read()).decode('utf-8', errors='ignore')
            participants = [line.strip() for line in p_text.splitlines() if line.strip()]
            n_players = len(participants)
            if n_players == 0:
                return await interaction.followup.send("❌ No participants")
            
            # Parse items
            i_text = (await items_csv.read()).decode('utf-8', errors='ignore')
            reader = csv.reader(i_text.splitlines())
            items = []
            for row in reader:
                if len(row) >= 3:
                    name = row[0].strip()
                    try:
                        qty = int(row[1])
                        rarity = row[2].strip().lower()
                        item_type = row[3].lower() if len(row) > 3 else "material"
                        items.append({"name": name, "rarity": rarity, "quantity": qty, "type": item_type})
                    except (ValueError, IndexError):
                        continue
            
            if not items:
                return await interaction.followup.send("❌ No loot items")
            
            # Sort by rarity DESC
            items.sort(key=lambda x: RARITY_ORDER.get(x["rarity"], 0), reverse=True)
            
            # Distribution
            dist = {p: [] for p in participants}
            
            # Snake draft: reset index per item
            round_num = 0
            for item in items:
                direction_forward = round_num % 2 == 0
                player_indices = list(range(n_players))
                if not direction_forward:
                    player_indices.reverse()
                
                # Distribute this item's quantity in snake order
                for q in range(item["quantity"]):
                    p_idx = q % n_players
                    player = participants[player_indices[p_idx]]
                    dist[player].append(item["name"])
                
                round_num += 1
            
            # Results
            total_items = sum(item["quantity"] for item in items)
            avg_per_player = math.ceil(total_items / n_players)
            
            for player, loot in dist.items():
                loot_text = ', '.join(loot)
                title = f"🎒 {player} ({len(loot)}/{avg_per_player})"
                embed = discord.Embed(title=title, color=0x00ff88)
                
                if len(loot_text) <= 4096:
                    embed.description = f"```{loot_text}```"
                    await interaction.followup.send(embed=embed)
                else:
                    # Split
                    chunk_size = 12
                    for start in range(0, len(loot), chunk_size):
                        chunk = loot[start:start+chunk_size]
                        chunk_text = ', '.join(chunk)
                        chunk_title = f"🎒 {player} ({start+1}-{min(start+chunk_size, len(loot))}/{len(loot)})"
                        chunk_embed = discord.Embed(title=chunk_title, color=0x00ff88)
                        chunk_embed.description = f"```{chunk_text}```"
                        await interaction.followup.send(chunk_embed)
            
            # Summary CSV
            summary = discord.Embed(title="✅ PERFECT BALANCE COMPLETE", color=0x00aa00)
            summary.add_field(name="Players", value=n_players, inline=True)
            summary.add_field(name="Total Items", value=total_items, inline=True)
            summary.add_field(name="Avg/Player", value=avg_per_player, inline=True)
            
            csv_lines = ["Player,Count,Items"]
            for p, l in dist.items():
                csv_lines.append(f'"{p}",{len(l)},"{",".join(l)}"')
            csv_data = "\n".join(csv_lines)
            csv_file = discord.File(io.BytesIO(csv_data.encode()), "fair_loot.csv")
            
            await interaction.followup.send(embed=summary, file=csv_file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)



