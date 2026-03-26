import discord
import aiohttp

def setup(bot):
    @bot.tree.command(name="price", description="Check WEMIX price in PHP")
    async def price_cmd(interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://api.coingecko.com/api/v3/simple/price?ids=wemix&vs_currencies=php') as resp:
                    data = await resp.json()
                    wemix_price = data['wemix']['php']
                    embed = discord.Embed(
                        title="💰 WEMIX Price", 
                        description=f"₱{wemix_price:,.2f}", 
                        color=discord.Color.green()
                    )
                    embed.set_footer(text="CoinGecko API")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed to fetch WEMIX price: {str(e)}", ephemeral=True)

