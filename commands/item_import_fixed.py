import csv
import io
import json
from datetime import datetime
from pathlib import Path

import discord

from .loot import bids, claims, reload_loot_items

LOOT_ITEMS_FILE = Path("loot_items.json")
BACKUP_DIR = Path("backups")
REQUIRED_COLUMNS = {"code", "name", "cost", "rule", "stock", "rarity"}


def _validate_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    errors = []
    parsed_items = []

    seen_codes = set()
    seen_names = set()

    for index, row in enumerate(rows, start=2):
        code = (row.get("code") or "").strip()
        name = (row.get("name") or "").strip()
        cost_text = (row.get("cost") or "").strip()
        rule = (row.get("rule") or "").strip()
        stock_text = (row.get("stock") or "999").strip()
        rarity = (row.get("rarity") or "common").strip().lower()

        if not code or not name or not cost_text or not rule:
            errors.append(f"Row {index}: code, name, cost, rule required.")
            continue

        if rarity not in ["common", "uncommon", "rare", "legendary"]:
            errors.append(f"Row {index}: rarity must be common/uncommon/rare/legendary.")
            continue

        try:
            cost = int(cost_text)
            if cost < 0:
                raise ValueError
        except ValueError:
            errors.append(f"Row {index}: cost must be non-negative integer.")
            continue

        try:
            stock = int(stock_text)
            if stock < 0:
                raise ValueError
        except ValueError:
            errors.append(f"Row {index}: stock must be non-negative integer.")
            continue

        code_key = code.lower()
        name_key = name.lower()

        if code_key in seen_codes:
            errors.append(f"Row {index}: duplicate code '{code}'.")
            continue
        if name_key in seen_names:
            errors.append(f"Row {index}: duplicate name '{name}'.")
            continue

        seen_codes.add(code_key)
        seen_names.add(name_key)

        parsed_items.append({
            "code": code,
            "name": name,
            "cost": cost,
            "rule": rule,
            "stock": stock,
            "rarity": rarity
        })

    if not parsed_items and not errors:
        errors.append("No valid items found.")

    return parsed_items, errors


def _find_unsafe_changes(new_items: list[dict]) -> list[str]:
    new_names = {item["name"] for item in new_items}
    active_names = set(claims.keys()) | set(bids.keys())

    missing_active_items = sorted(active_names - new_names)
    if not missing_active_items:
        return []

    return [
        "⚠️ Active claim/bid items missing from CSV:",
        *[f"  • {item_name}" for item_name in missing_active_items],
    ]


def _backup_current_loot_file() -> Path | None:
    if not LOOT_ITEMS_FILE.exists():
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"loot_items-{timestamp}.json"
    backup_path.write_text(LOOT_ITEMS_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    return backup_path


def _save_loot_items(items: list[dict]):
    LOOT_ITEMS_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")


def setup(bot):
    @bot.tree.command(name="impitems", description="Import loot items from CSV (code,name,cost,rule,stock,rarity)")
    async def import_items_cmd(interaction: discord.Interaction, file: discord.Attachment):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message("❌ Mod/Elder only.", ephemeral=True)
            return

        if not file.filename.lower().endswith(".csv"):
            await interaction.response.send_message("❌ Upload CSV.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            raw_bytes = await file.read()
            raw_text = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            await interaction.followup.send("❌ UTF-8 CSV required.", ephemeral=True)
            return

        reader = csv.DictReader(io.StringIO(raw_text))
        rows = list(reader)

        items, errors = _validate_rows(rows)

        if errors:
            await interaction.followup.send("❌ " + "\n".join(errors[:10]), ephemeral=True)
            return

        warnings = _find_unsafe_changes(items)
        if warnings:
            await interaction.followup.send("\n".join(warnings) + "\n\nContinue? Reply 'force-import'.", ephemeral=True)
            return

        backup_path = _backup_current_loot_file()
        _save_loot_items(items)
        reload_loot_items()

        backup_text = f"\n🗂️ Backup: `{backup_path.name}`" if backup_path else ''
        await interaction.followup.send(
            f"✅ **{len(items)}** items imported from `{file.filename}`{backup_text}\n🔄 Reloaded live.",
            ephemeral=True
        )
