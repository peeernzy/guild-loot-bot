import discord
from .loot import loot_meta, reload_loot_items, claim_aliases, bid_aliases
from .points import using_postgres, get_sqlite_connection, get_postgres_connection

def find_item(name_or_code):
    """Find item name by name or code/alias lookup."""
    item_lookup = name_or_code.strip().lower()
    # Check meta keys
    for name, meta in loot_meta.items():
        if item_lookup == name.lower():
            return name
    # Check aliases
    for alias_map in (claim_aliases, bid_aliases):
        if item_lookup in alias_map:
            return alias_map[item_lookup]
    return None

def get_stock(item_name):
    """Get current stock."""
    meta = loot_meta.get(item_name, {})
    stock = meta.get('stock', 999)
    return stock

def setup(bot):
    @bot.tree.command(name="stock", description="Check item stock/inventory.")
    async def stock_cmd(interaction: discord.Interaction, item: str):
        await interaction.response.defer(ephemeral=True)
        target_item = find_item(item)
        if not target_item:
            await interaction.followup.send(f"❌ Item '{item}' not found. Use `/items`.")
            return

        stock = get_stock(target_item)
        stock_display = f"{stock} left" if stock < 999 else "Unlimited"
        await interaction.followup.send(f"📦 **{target_item}**: **{stock_display}**")

    @bot.tree.command(name="restock", description="Restock item (Mod/Elder only)")
    async def restock_cmd(interaction: discord.Interaction, item: str, qty: int):
        if not any(r.name in {"Moderator", "Elder"} for r in interaction.user.roles):
            await interaction.response.send_message("❌ Mod/Elder only.", ephemeral=True)
            return

        if qty <= 0:
            await interaction.response.send_message("❌ Qty must be positive.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        target_item = find_item(item)
        if not target_item:
            await interaction.followup.send(f"❌ Item '{item}' not found. Use `/items`.")
            return

        # Update DB stock
        old_stock = get_stock(target_item)
        if using_postgres():
            with get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE items SET stock = GREATEST(0, stock + %s) WHERE name = %s", (qty, target_item))
                    changed = cur.rowcount > 0
                    cur.execute("SELECT stock FROM items WHERE name = %s", (target_item,))
                    new_stock = cur.fetchone()[0]
            conn.commit()
        else:
            with get_sqlite_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE items SET stock = MAX(0, stock + ?) WHERE name = ?", (qty, target_item))
                changed = cur.rowcount > 0
                cur.execute("SELECT stock FROM items WHERE name = ?", (target_item,))
                new_stock = cur.fetchone()[0]
            conn.commit()

        if not changed:
            await interaction.followup.send(f"❌ Item '{target_item}' not in DB.")
            return

        reload_loot_items()
        await interaction.followup.send(f"✅ **{target_item}** stock: {old_stock} → **{new_stock}** (DB updated, persists restart)")
