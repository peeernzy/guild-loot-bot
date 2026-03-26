import discord
import aiohttp
import asyncio

def setup(bot):
    @bot.tree.command(name="coins", description="Check WEMIX & USDT price in PHP")
    async def coins_cmd(interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://api.coingecko.com/api/v3/simple/price?ids=wemix,tether&vs_currencies=php') as resp:
                    data = await resp.json()
                    wemix_price = data['wemix']['php']
                    usdt_price = data['tether']['php']
                
                embed = discord.Embed(
                    title="💰 WEMIX & USDT Price",
                    description=f"**WEMIX:** ₱{wemix_price:,.2f} PHP\n**USDT:** ₱{usdt_price:,.2f} PHP",
                    color=discord.Color.green()
                )
                embed.set_footer(text="Data from CoinGecko API")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed to fetch price: {str(e)}", ephemeral=True)
