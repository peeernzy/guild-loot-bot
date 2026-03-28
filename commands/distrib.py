import discord
from discord import app_commands
import csv
import random
import io
import math

RARITY_ORDER = {"common":1, "uncommon":2, "rare":3, "epic":4, "legend":5, "mythic":6}

def snake_order(players, forward=True):
    """Round robin snake draft order."""
    if forward:
        return players
    return list(reversed(players))

def setup(bot):
    @bot.tree.command(name="distribute", description="Balanced raid loot distribution")
    @app_commands.describe(participants_file="Players CSV (one name per line)", items_csv="Loot CSV")
    async def distribute_cmd(interaction: discord.Interaction, participants_file: discord.Attachment, items_csv: discord.Attachment):
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Mod/Elder only", ephemeral=True)
        
        await interaction.response.defer()
        
        try:
            # Parse participants
            p_text = (await participants_file.read()).decode('utf-8', errors='ignore')
            participants = [line.strip() for line in p_text.splitlines() if line.strip()]
            if not participants:
                return await interaction.followup.send("❌ No participants found")
            
            n_players = len(participants)
            
            # Parse items
            i_text = (await items_csv.read()).decode('utf-8', errors='ignore')
            reader = csv.reader(io.StringIO(i_text))
            items = []
            for row in reader:
                if len(row) >= 3:
                    name = row[0].strip()
                    try:
                        qty = int(float(row[1]))
                        rarity = row[2].strip().lower()
                        item_type = row[3].strip().lower() if len(row) > 3 else "material"
                        if qty > 0:
                            items.append({"name": name, "rarity": rarity, "quantity": qty, "type": item_type})
                    except ValueError:
                        continue
            
            if not items:
                return await interaction.followup.send("❌ No valid loot items found")
            
            # Sort items by rarity DESC
            items.sort(key=lambda x: RARITY_ORDER.get(x["rarity"], 0), reverse=True)
            
            # Distribution dict
            dist = {player: [] for player in participants}
            
            # Perfect round-robin snake draft
            round_num = 0
            all_items_assigned = 0
            
            for item in items:
                direction_forward = round_num % 2 == 0
                player_order = snake_order(participants, direction_forward)
                
                for _ in range(item["quantity"]):
                    player = player_order[all_items_assigned % n_players]
                    dist[player].append(item["name"])
                    all_items_assigned += 1
                
                round_num += 1
            
            # Send individual results (FULL lists)
            total_items = sum(item["quantity"] for item in items)
            for player, loot in dist.items():
                loot_str = ", ".join(loot)
                embed = discord.Embed(title=f"🎒 {player}'s Loot ({len(loot)}/{total_items//n_players + 1})", color=0x00ff88)
                
                if len(loot_str) <= 4096:
                    embed.description = f"```\n{loot_str}\n```"
                    await interaction.followup.send(embed=embed)
                else:
                    # Split long lists across multiple embeds
                    for i in range(0, len(loot), 15):  # ~15 items per message
                        chunk = loot[i:i+15]
                        chunk_str = ", ".join(chunk)
                        chunk_embed = discord.Embed(title=f"🎒 {player} ({i+1}-{min(i+15, len(loot))}/{len(loot)})", color=0x00ff88)
                        chunk_embed.description = f"```\n{chunk_str}\n```"
                        await interaction.followup.send(embed=chunk_embed)
            
            # Summary + CSV
            summary_embed = discord.Embed(title="🎉 RAID DISTRIBUTION COMPLETE", color=0x00aa00)
            avg_items = math.ceil(total_items / n_players)
            summary_embed.add_field(name="Players", value=str(n_players), inline=True)
            summary_embed.add_field(name="Total Items", value=str(total_items), inline=True)
            summary_embed.add_field(name="Avg/Player", value=str(avg_items), inline=True)
            
            csv_lines = ["Player,Loot Count,Items"]
            for player, loot in dist.items():
                items_csv = ",".join(loot)
                csv_lines.append(f'"{player}",{len(loot)},"{items_csv}"')
            
            csv_content = "\n".join(csv_lines)
            csv_file = discord.File(io.BytesIO(csv_content.encode('utf-8')), "balanced_loot.csv")
            
            await interaction.followup.send(embed=summary_embed, file=csv_file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


