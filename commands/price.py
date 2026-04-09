import discord
import aiohttp
import asyncio
import os
from datetime import datetime
from discord.ext import commands
from discord import app_commands

CMC_API_KEY = os.getenv("CMC_API_KEY", "YOUR_CMC_API_KEY")

class PriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="price", description="Check WEMIX & USDT price in PHP and USD")
    async def price_cmd(self, interaction: discord.Interaction):
        # Role-based cooldown: skip for Moderator/Elder
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        # Apply cooldown only if not Moderator/Elder
        if not has_permission:
            # Check if user is on cooldown
            cooldown_key = f"price:{interaction.user.id}"
            if hasattr(self.bot, "cooldowns") and cooldown_key in self.bot.cooldowns:
                remaining = self.bot.cooldowns[cooldown_key] - datetime.now().timestamp()
                if remaining > 0:
                    await interaction.response.send_message(
                        f"⏳ Please wait {int(remaining)}s before using this command again.",
                        ephemeral=True
                    )
                    return
            # Set cooldown (5 minutes = 300s)
            if not hasattr(self.bot, "cooldowns"):
                self.bot.cooldowns = {}
            self.bot.cooldowns[cooldown_key] = datetime.now().timestamp() + 300

        async with aiohttp.ClientSession() as session:
            async def fetch_prices(convert_currency):
                url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
                params = {"symbol": "WEMIX,USDT", "convert": convert_currency}
                headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
                async with session.get(url, params=params, headers=headers) as resp:
                    return await resp.json()

            try:
                # Fetch PHP prices
                data_php = await fetch_prices("PHP")
                # Fetch USD prices
                data_usd = await fetch_prices("USD")

                # Graceful fallback if one fails
                wemix_php = usdt_php = wemix_usd = usdt_usd = None

                if "data" in data_php:
                    wemix_php = data_php["data"]["WEMIX"]["quote"]["PHP"]["price"]
                    usdt_php  = data_php["data"]["USDT"]["quote"]["PHP"]["price"]

                if "data" in data_usd:
                    wemix_usd = data_usd["data"]["WEMIX"]["quote"]["USD"]["price"]
                    usdt_usd  = data_usd["data"]["USDT"]["quote"]["USD"]["price"]

                # Build embed with whatever data we have
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                desc = ""
                if wemix_php: desc += f"📌 WEMIX → PHP: ₱{wemix_php:,.2f}\n"
                if wemix_usd: desc += f"📌 WEMIX → USD: ${wemix_usd:,.2f}\n\n"
                if usdt_php:  desc += f"📌 USDT → PHP: ₱{usdt_php:,.2f}\n"
                if usdt_usd:  desc += f"📌 USDT → USD: ${usdt_usd:,.2f}\n"

                if desc:
                    embed = discord.Embed(
                        title="💰 Coin Prices",
                        description=desc,
                        color=discord.Color.green()
                    )
                    embed.set_footer(text=f"Data from CoinMarketCap API • Fetched at {timestamp}")
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("❌ No price data available.")

            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Failed to fetch prices: {str(e)}"
                )

async def setup(bot):
    await bot.add_cog(PriceCog(bot))
