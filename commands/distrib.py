import discord
from discord import app_commands
import csv
import io
import math
import random
from collections import Counter

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
            
            # Sort: equipment first, then rarity DESC
            items.sort(
                key=lambda x: (
                    0 if x["type"] == "equipment" else 1,
                    -RARITY_ORDER.get(x["rarity"], 0)
                )
            )
            
            # Distribution
            dist = {p: [] for p in participants}
            player_index = 0
            direction_forward = True
            
            for item in items:
                if item["type"] == "equipment":
                    # Equipment → snake draft
                    for q in range(item["quantity"]):
                        player = participants[player_index]
                        dist[player].append(item["name"])
                        
                        # Snake movement
                        if direction_forward:
                            player_index += 1
                            if player_index == n_players:
                                player_index -= 1
                                direction_forward = False
                        else:
                            player_index -= 1
                            if player_index < 0:
                                player_index = 0
                                direction_forward = True
                
                elif item["type"] == "material":
                    rarity = item["rarity"]
                    
                    if rarity == "rare":
                        qty_left = item["quantity"]
                        rare_cycle = set()  # track who already got rare material in this cycle
                        
                        while qty_left > 0:
                            # Reset cycle if everyone has received rare material
                            if len(rare_cycle) == n_players:
                                rare_cycle.clear()
                            
                            # Skip players who already got rare material in this cycle
                            while participants[player_index] in rare_cycle:
                                player_index = (player_index + 1) % n_players
                            
                            player = participants[player_index]
                            # Batch size: strictly 2–4
                            give_count = min(qty_left, random.randint(2, 4))
                            
                            dist[player].extend([item["name"]] * give_count)
                            qty_left -= give_count
                            
                            # Mark player as having received rare material this cycle
                            rare_cycle.add(player)
                            
                            # Move to next player
                            player_index = (player_index + 1) % n_players
                    
                    elif rarity in {"common", "uncommon"}:
                        if item["quantity"] > 4:
                            # Split stack into halves
                            half1 = item["quantity"] // 2
                            half2 = item["quantity"] - half1

                            # First player gets half1
                            player1 = participants[player_index]
                            dist[player1].extend([item["name"]] * half1)

                            # Advance snake index
                            if direction_forward:
                                player_index += 1
                                if player_index == n_players:
                                    player_index -= 1
                                    direction_forward = False
                            else:
                                player_index -= 1
                                if player_index < 0:
                                    player_index = 0
                                    direction_forward = True

                            # Second player gets half2
                            player2 = participants[player_index]
                            dist[player2].extend([item["name"]] * half2)

                            # Advance snake index again
                            if direction_forward:
                                player_index += 1
                                if player_index == n_players:
                                    player_index -= 1
                                    direction_forward = False
                            else:
                                player_index -= 1
                                if player_index < 0:
                                    player_index = 0
                                    direction_forward = True
                        else:
                            # Whole stack to one player
                            player = participants[player_index]
                            dist[player].extend([item["name"]] * item["quantity"])

                            # Advance snake index once
                            if direction_forward:
                                player_index += 1
                                if player_index == n_players:
                                    player_index -= 1
                                    direction_forward = False
                            else:
                                player_index -= 1
                                if player_index < 0:
                                    player_index = 0
                                    direction_forward = True
            
            # Results
            total_items = sum(item["quantity"] for item in items)
            avg_per_player = math.ceil(total_items / n_players)
            
            for player, loot in dist.items():
                counts = Counter(loot)
                loot_text = '\n'.join(
                    f"{item}({qty})" if qty > 1 else item
                    for item, qty in counts.items()
                )
                
                title = f"🎒 {player} ({len(loot)}/{avg_per_player})"
                embed = discord.Embed(title=title, color=0x00ff88)
                
                if len(loot_text) <= 4096:
                    embed.description = f"```{loot_text}```"
                    await interaction.followup.send(embed=embed)
                else:
                    # Split by chunks of 12 items
                    chunk_size = 12
                    loot_items = list(counts.items())
                    for start in range(0, len(loot_items), chunk_size):
                        chunk = loot_items[start:start+chunk_size]
                        chunk_text = '\n'.join(
                            f"{item}({qty})" if qty > 1 else item
                            for item, qty in chunk
                        )
                        chunk_title = f"🎒 {player} ({start+1}-{min(start+chunk_size, len(loot_items))}/{len(loot_items)})"
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
                counts = Counter(l)
                grouped_items = '\n'.join(
                    f"{item}({qty})" if qty > 1 else item
                    for item, qty in counts.items()
                )
                csv_lines.append(f'"{p}",{len(l)},"{grouped_items}"')
            
            csv_data = "\n".join(csv_lines)
            csv_file = discord.File(io.BytesIO(csv_data.encode()), "fair_loot.csv")
            
            await interaction.followup.send(embed=summary, file=csv_file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)
