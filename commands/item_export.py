import io
import discord
from .points import using_postgres, get_sqlite_connection, get_postgres_connection
from .items_db import load_loot_items_from_db

def _build_csv_rows(items: list[dict]) -> str:
    lines = ["code,name,cost,rule,stock,rarity"]
    claim_count = 0
    bid_count = 0
    for item in items:
        rule = item["rule"]
        if str(rule).startswith("Bidding"):
            bid_count += 1
            code = str(bid_count)
        else:
            claim_count += 1
            code = str(claim_count)
        name = str(item["name"]).replace('"', '""')
        cost = str(item["cost"])
        rule_str = str(rule).replace('"', '""')
        stock = str(item["stock"])
        rarity = str(item["rarity"]).replace('"', '""')
        line = f'"{code}","{name}","{cost}","{rule_str}","{stock}","{rarity}"'
        lines.append(line)
    return "\n".join(lines)

def setup(bot):
    @bot.tree.command(name="inventory_export", description="Export loot items to CSV (compatible with /inventory_import)")
    async def inventory_export_cmd(interaction: discord.Interaction):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message(
                "❌ Only Moderators and Elders can export item lists.",
                ephemeral=True
            )
            return

        items = []
        if using_postgres():
            with get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT name, cost, rule, stock, rarity FROM items ORDER BY name")
                    rows = cur.fetchall()
                    for row in rows:
                        items.append({"name": row[0], "cost": row[1], "rule": row[2], "stock": row[3], "rarity": row[4]})
        else:
            with get_sqlite_connection() as conn:
                rows = conn.execute("SELECT name, cost, rule, stock, rarity FROM items ORDER BY name").fetchall()
                for row in rows:
                    items.append({"name": row[0], "cost": row[1], "rule": row[2], "stock": row[3], "rarity": row[4]})
        
        if not items:
            await interaction.response.send_message("❌ No items in DB. Import first with /inventory_import.", ephemeral=True)
            return
        
        csv_content = _build_csv_rows(items)
        file_buffer = io.BytesIO(csv_content.encode("utf-8"))

        await interaction.response.send_message(
            f"📦 **Exported {len(items)} items** from DB as CSV.",
            file=discord.File(file_buffer, filename="loot_items_export.csv"),
            ephemeral=True
        )

