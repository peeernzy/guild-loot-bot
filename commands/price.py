import discord
import aiohttp
import asyncio
from datetime import datetime
from discord.ext import commands
from discord import app_commands

CMC_API_KEY = "223c820789d84b9ea99697079111d0b5"  # replace with your actual key

class PriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="price", description="Check WEMIX & USDT price in PHP and USD")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)  # 1 use per 10s per user
    async def price_cmd(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async def fetch_prices():
                url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
                params = {
                    "symbol": "WEMIX,USDT",
                    "convert": "PHP,USD"
                }
                headers = {
                    "X-CMC_PRO_API_KEY": CMC_API_KEY
                }
                async with session.get(url, params=params, headers=headers) as resp:
                    return await resp.json()

            try:
                data = await fetch_prices()

                # Retry once if missing data
                if "data" not in data or not data["data"].get("WEMIX") or not data["data"].get("USDT"):
                    await asyncio.sleep(1)
                    data = await fetch_prices()

                wemix_data = data["data"].get("WEMIX", {})
                usdt_data = data["data"].get("USDT", {})

                wemix_quote = wemix_data.get("quote", {})
                usdt_quote = usdt_data.get("quote", {})

                wemix_php = wemix_quote.get("PHP", {}).get("price")
                wemix_usd = wemix_quote.get("USD", {}).get("price")
                usdt_php = usdt_quote.get("PHP", {}).get("price")
                usdt_usd = usdt_quote.get("USD", {}).get("price")

                if all(v is not None for v in [wemix_php, wemix_usd, usdt_php, usdt_usd]):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
                    embed.set_footer(text=f"Data from CoinMarketCap API • Fetched at {timestamp}")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Price data not found.", ephemeral=True)

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Failed to fetch prices: {str(e)}", ephemeral=True
                )

async def setup(bot):
    await bot.add_cog(PriceCog(bot))
