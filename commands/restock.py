import discord
import json
from pathlib import Path
from .loot import loot_meta, reload_loot_items, claim_aliases, bid_aliases

LOOT_ITEMS_FILE = Path("loot_items.json")

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

def update_stock(item_name, qty_change):
    """Update stock for item, persist to JSON."""
    try:
        with open(LOOT_ITEMS_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return False, "loot_items.json not found."

    items = data.get('items', [])
    updated = False
    for item in items:
        if item['name'] == item_name:
            old_stock = item.get('stock', 999)
            item['stock'] = max(0, old_stock + qty_change)
            updated = True
            break

    if not updated:
        return False, f"Item '{item_name}' not found."

    with open(LOOT_ITEMS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    # Reload globals
    reload_loot_items()
    return True, f"✅ {item_name} stock: {old_stock} → {item['stock']}"

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

        success, msg = update_stock(target_item, qty)
        if success:
            await interaction.followup.send(msg)
        else:
            await interaction.followup.send(msg)
