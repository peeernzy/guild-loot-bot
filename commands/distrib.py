import discord
from discord import app_commands
import csv
import io
import math
import random
from collections import Counter
from datetime import datetime, timedelta, timezone

RARITY_ORDER = {"common":1, "uncommon":2, "rare":3, "epic":4, "legend":5, "mythic":6}

def setup(bot):
    @bot.tree.command(name="distribute", description="PERFECT BALANCED loot distribution")
    @app_commands.describe(participants_file="Players CSV (one name per line)", items_csv="Loot CSV")
    async def distribute_cmd(interaction: discord.Interaction, participants_file: discord.Attachment, items_csv: discord.Attachment):
        # ✅ Defer immediately
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
            reader = csv.DictReader(io.StringIO(i_text))
            items = []
            for row in reader:
                row_lower = {k.lower(): v for k, v in row.items()}
                name = (row_lower.get("name") or "").strip()
                qty_str = row_lower.get("quantity") or row_lower.get("qty") or row_lower.get("count") or ""
                rarity = (row_lower.get("rarity") or "").strip().lower()
                item_type = (row_lower.get("type") or "material").strip().lower()
                try:
                    qty = int(qty_str)
                    if name and qty >= 0 and rarity:
                        items.append({"name": name, "rarity": rarity, "quantity": qty, "type": item_type})
                except ValueError:
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
                        dist[player].append((item["name"], item["rarity"]))

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
                        rare_cycle = set()
                        while qty_left > 0:
                            if len(rare_cycle) == n_players:
                                rare_cycle.clear()
                            while participants[player_index] in rare_cycle:
                                player_index = (player_index + 1) % n_players
                            player = participants[player_index]
                            give_count = min(qty_left, random.randint(2, 4))
                            dist[player].extend([(item["name"], rarity)] * give_count)
                            qty_left -= give_count
                            rare_cycle.add(player)
                            player_index = (player_index + 1) % n_players

                    elif rarity in {"common", "uncommon"}:
                        if item["quantity"] > 4:
                            half1 = item["quantity"] // 2
                            half2 = item["quantity"] - half1

                            player1 = participants[player_index]
                            dist[player1].extend([(item["name"], rarity)] * half1)

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

                            player2 = participants[player_index]
                            dist[player2].extend([(item["name"], rarity)] * half2)

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
                            player = participants[player_index]
                            dist[player].extend([(item["name"], rarity)] * item["quantity"])

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
                sorted_items = sorted(counts.items(), key=lambda x: -RARITY_ORDER.get(x[0][1], 0))
                loot_text = '\n'.join(
                    f"{item}({qty})" if qty > 1 else item
                    for (item, rarity), qty in sorted_items
                )

                title = f"🎒 {player} ({len(loot)}/{avg_per_player})"
                embed = discord.Embed(title=title, color=0x00ff88)
                embed.description = f"```{loot_text}```"
                await interaction.followup.send(embed=embed)

            # Summary CSV
            summary = discord.Embed(title="✅ PERFECT BALANCE COMPLETE", color=0x00aa00)
            summary.add_field(name="Players", value=n_players, inline=True)
            summary.add_field(name="Total Items", value=total_items, inline=True)
            summary.add_field(name="Avg/Player", value=avg_per_player, inline=True)

            csv_lines = ["Player,Items"]
            for p, l in dist.items():
                counts = Counter(l)
                sorted_items = sorted(counts.items(), key=lambda x: -RARITY_ORDER.get(x[0][1], 0))
                grouped_items = '\n'.join(
                    f"{item}({qty})" if qty > 1 else item
                    for (item, rarity), qty in sorted_items
                )
                csv_lines.append(f'"{p}","{grouped_items}"')

            csv_data = "\n".join(csv_lines)
            csv_file = discord.File(io.BytesIO(csv_data.encode()), "fair_loot.csv")

            await interaction.followup.send(embed=summary, file=csv_file)

            # ✅ Final announcement embed with clan emblem, motivational line, bold values, centered separator, and emojis
            gmt8 = timezone(timedelta(hours=8))
            now = datetime.now(gmt8).strftime("%A, %B %d, %Y %I:%M:%S %p GMT+8")

            announcement = discord.Embed(
                title="✅ 🛡️ 📢 Clan Warehouse Loot",
                description="@everyone All loot from the Clan Warehouse is ready.\n\n"
                            "Please wait for the Leader and Elders to handle the final distribution.\n\n"
                            "✨ Great teamwork, everyone! ✨",
                color=0x00ff00
            )
            announcement.add_field(name="Total Items Prepared", value=f"**{total_items}**", inline=True)
            announcement.add_field(name="Players", value=f"**{n_players}**", inline=True)
            announcement.set_footer(text=f"───────────────\n📅 {now}")
            await interaction.followup.send(embed=announcement)

        except Exception as e:
            await interaction.followup.send(f"❌ {e}", ephemeral=True)
