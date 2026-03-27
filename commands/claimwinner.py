import discord
import random
from commands.loot import claims, loot_costs
from commands.utils import spend_points, can_spend
from commands.logger import log_event

LOOT_CHANNEL_ID = 1485956297227763752  # from loot.py

def setup(bot):
    @bot.tree.command(name="claimwinner", description="Select random winner for claimed item with 1-100 roll")
    async def claim_winner_cmd(interaction: discord.Interaction, item: str):
        # Find item from aliases
        from commands.loot import claim_aliases, bid_aliases
        lookup = item.lower()
        target_item = None
        target_item = claim_aliases.get(lookup)
        if not target_item:
            target_item = bid_aliases.get(lookup)
        if not target_item:
            await interaction.response.send_message("❌ Item not found. Use `/items`", ephemeral=True)
            return
        if not target_item:
            await interaction.response.send_message("❌ Item not found.", ephemeral=True)
            return

        data = claims.get(target_item, {})
        players = data.get("players", [])
        if not players:
            await interaction.response.send_message("❌ No players claimed this item.", ephemeral=True)
            return

        guild = interaction.guild
        rolls = {}
        embed = discord.Embed(title=f"🎲 Spin Result for {target_item}", color=discord.Color.gold())
        roll_list = []

        for pid in players:
            player = guild.get_member(pid)
            if player:
                roll = random.randint(1, 100)
                rolls[pid] = roll
                roll_list.append(f"{roll}: {player.display_name}")

        roll_list.sort(key=lambda x: int(x.split(':')[0]), reverse=True)
        embed.description = "\n".join(roll_list[:5])  # top 5

        if roll_list:
            top_roll_str, winner_name = roll_list[0].split(': ', 1)
            winner_id = next(pid for pid, r in rolls.items() if r == int(top_roll_str))
            winner = guild.get_member(winner_id)
            cost = loot_costs.get(target_item, {}).get("cost", 0)
            if can_spend(winner_id, cost, target_item):
                spend_points(winner_id, cost, target_item)
                log_event("spin_win", winner_id, target_item, cost)
                embed.add_field(name="🏆 Winner", value=f"{winner.mention} | Roll: {top_roll_str}", inline=False)
                del claims[target_item]
            else:
                embed.add_field(name="⚠️ Winner cannot pay", value=f"{winner.mention} Roll: {top_roll_str}", inline=False)

        loot_channel = bot.get_channel(LOOT_CHANNEL_ID)
        if loot_channel:
            await loot_channel.send(embed=embed)

        await interaction.response.send_message("✅ Winner announced!", ephemeral=True)

