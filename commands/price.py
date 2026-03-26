import discord
import aiohttp
import asyncio
from datetime import datetime
from discord.ext import commands
from discord import app_commands

class PriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="price", description="Check WEMIX & USDT price in PHP and USD")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)  # 1 use per 10s per user
    async def price_cmd(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async def fetch_prices():
                async with session.get(
                    'https://api.coingecko.com/api/v3/simple/price?ids=wemix,tether&vs_currencies=php,usd'
                ) as resp:
                    return await resp.json()

            try:
                # First attempt
                data = await fetch_prices()

                # Retry once if missing data
                if not data.get('wemix') or not data.get('tether'):
                    await asyncio.sleep(1)
                    data = await fetch_prices()

                wemix_data = data.get('wemix', {})
                usdt_data = data.get('tether', {})

                wemix_php = wemix_data.get('php')
                wemix_usd = wemix_data.get('usd')
                usdt_php = usdt_data.get('php')
                usdt_usd = usdt_data.get('usd')

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
                    embed.set_footer(text=f"Data from CoinGecko API • Fetched at {timestamp}")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Price data not found.", ephemeral=True)

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Failed to fetch prices: {str(e)}", ephemeral=True
                )

async def setup(bot):
    await bot.add_cog(PriceCog(bot))
