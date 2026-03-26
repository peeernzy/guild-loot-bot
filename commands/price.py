import discord
import aiohttp

def setup(bot):
    @bot.tree.command(name="price", description="Check WEMIX & USDT price in PHP and USD")
    async def price_cmd(interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            try:
                # Fetch WEMIX and USDT prices in PHP + USD
                async with session.get(
                    'https://api.coingecko.com/api/v3/simple/price?ids=wemix,tether&vs_currencies=php,usd'
                ) as resp:
                    data = await resp.json()

                    wemix_data = data.get('wemix')
                    usdt_data = data.get('tether')

                    if wemix_data and usdt_data:
                        wemix_php = wemix_data.get('php')
                        wemix_usd = wemix_data.get('usd')
                        usdt_php = usdt_data.get('php')
                        usdt_usd = usdt_data.get('usd')

                        embed = discord.Embed(
                            title="💰 Coin Prices",
                            description=(
                                f"📌 WEMIX → PHP: ₱{wemix_php:,.2f}\n"
                                f"📌 WEMIX → USD: ${wemix_usd:,.2f}\n\n"
                                f"📌 USDT → PHP: ₱{usdt_php:,.2f}\n"
                                f"📌 USDT → USD: ${usdt_usd:,.2f}"
                            ),
                            color=discord.Color.green()
                        )
                        embed.set_footer(text="Data from CoinGecko API")
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                    else:
                        await interaction.response.send_message("❌ Price data not found.", ephemeral=True)

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Failed to fetch prices: {str(e)}", ephemeral=True
                )
