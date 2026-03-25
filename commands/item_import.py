import csv
import io
import json
from datetime import datetime
from pathlib import Path

import discord

from .loot import bids, claims, reload_loot_items

LOOT_ITEMS_FILE = Path("loot_items.json")
BACKUP_DIR = Path("backups")
REQUIRED_COLUMNS = {"code", "name", "cost", "rule", "aliases"}


def _normalize_aliases(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    return [alias.strip() for alias in raw_value.split("|") if alias.strip()]


def _validate_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    errors = []
    parsed_items = []

    seen_codes = set()
    seen_names = set()
    seen_aliases = set()

    for index, row in enumerate(rows, start=2):
        code = (row.get("code") or "").strip()
        name = (row.get("name") or "").strip()
        cost_text = (row.get("cost") or "").strip()
        rule = (row.get("rule") or "").strip()
        aliases = _normalize_aliases((row.get("aliases") or "").strip())

        if not code or not name or not cost_text or not rule:
            errors.append(f"Row {index}: code, name, cost, and rule are required.")
            continue

        try:
            cost = int(cost_text)
            if cost < 0:
                raise ValueError
        except ValueError:
            errors.append(f"Row {index}: cost must be a valid non-negative integer.")
            continue

        code_key = code.lower()
        name_key = name.lower()

        if code_key in seen_codes:
            errors.append(f"Row {index}: duplicate code '{code}'.")
            continue
        if name_key in seen_names:
            errors.append(f"Row {index}: duplicate item name '{name}'.")
            continue

        seen_codes.add(code_key)
        seen_names.add(name_key)

        row_aliases = set()
        for alias in aliases:
            alias_key = alias.lower()
            if alias_key in seen_aliases or alias_key in row_aliases:
                errors.append(f"Row {index}: duplicate alias '{alias}'.")
                continue
            if alias_key == code_key:
                errors.append(f"Row {index}: alias '{alias}' cannot match the item code.")
                continue
            row_aliases.add(alias_key)

        if any(message.startswith(f"Row {index}:") for message in errors):
            continue

        seen_aliases.update(row_aliases)
        parsed_items.append(
            {
                "code": code,
                "name": name,
                "cost": cost,
                "rule": rule,
                "aliases": aliases,
            }
        )

    if not parsed_items and not errors:
        errors.append("The CSV does not contain any valid item rows.")

    return parsed_items, errors


def _find_unsafe_changes(new_items: list[dict]) -> list[str]:
    new_names = {item["name"] for item in new_items}
    active_names = set(claims.keys()) | set(bids.keys())

    missing_active_items = sorted(active_names - new_names)
    if not missing_active_items:
        return []

    return [
        "Import blocked because these active claim/bid items are missing from the CSV:",
        *[f"- {item_name}" for item_name in missing_active_items],
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
    payload = {"items": items}
    LOOT_ITEMS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def setup(bot):
    @bot.tree.command(name="importitems", description="Import and replace loot items from a CSV file")
    async def import_items_cmd(interaction: discord.Interaction, file: discord.Attachment):
        allowed_roles = {"Moderator", "Elder"}
        has_permission = any(role.name in allowed_roles for role in interaction.user.roles)

        if not has_permission:
            await interaction.response.send_message(
                "❌ Only Moderators and Elders can import item lists.",
                ephemeral=True
            )
            return

        if not file.filename.lower().endswith(".csv"):
            await interaction.response.send_message(
                "❌ Please upload a CSV file.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            raw_bytes = await file.read()
            raw_text = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            await interaction.followup.send(
                "❌ The CSV file must be UTF-8 encoded.",
                ephemeral=True
            )
            return

        reader = csv.DictReader(io.StringIO(raw_text))
        headers = set(reader.fieldnames or [])

        missing_columns = sorted(REQUIRED_COLUMNS - headers)
        if missing_columns:
            await interaction.followup.send(
                "❌ Missing required CSV columns: " + ", ".join(missing_columns),
                ephemeral=True
            )
            return

        rows = list(reader)
        items, errors = _validate_rows(rows)

        if errors:
            await interaction.followup.send(
                "❌ Import failed:\n" + "\n".join(errors[:15]),
                ephemeral=True
            )
            return

        safety_warnings = _find_unsafe_changes(items)
        if safety_warnings:
            await interaction.followup.send(
                "❌ " + "\n".join(safety_warnings),
                ephemeral=True
            )
            return

        backup_path = _backup_current_loot_file()
        _save_loot_items(items)
        reload_loot_items()

        backup_message = (
            f"\n🗂️ Backup created: `{backup_path.as_posix()}`"
            if backup_path else
            "\n🗂️ No previous loot file was found, so no backup was needed."
        )

        await interaction.followup.send(
            f"✅ Imported {len(items)} loot items from `{file.filename}`."
            f"{backup_message}\n🔄 Loot commands now use the updated item list.",
            ephemeral=True
        )
